# Orchestrator Workflows (State Machine + Run Log)

This document makes the generation lifecycle deterministic so backend, UI, and MCP tool servers can be implemented in parallel.

---

## 1) Entities

### 1.1 Generation Run
A **run** is one end-to-end execution of a blueprint to produce a paper.

**Key fields** (recommended):
- `run_id` (UUID)
- `tenant_id`
- `blueprint_id`
- `scope` (board/standard/subject/language)
- `mode` (strict|free)
- `status`
- `created_at`, `started_at`, `completed_at`
- `config` (thresholds, token budgets, retry policy)
- `metrics` (tokens, cost, latency)

### 1.2 Run Item
A **run item** is one question slot to fill.

**Key fields** (recommended):
- `item_id` (UUID)
- `run_id`
- `slot` (marks, section, difficulty, taxonomy tags)
- `retrieval` (query inputs + context pack summary)
- `draft` (model output)
- `evaluation` (scores + reasons)
- `teacher_review` (status + edits + reason)
- `status`

### 1.3 Run Event Log (append-only)
Every important transition emits a structured event.

---

## 2) Status Model

### 2.1 Run Statuses
Use a strict run-level state machine:

- `created` → run exists, not yet started
- `planning` → validating scope + expanding blueprint slots
- `generating` → items are being processed
- `awaiting_review` → at least one item requires teacher action
- `ready_to_export` → all required items approved
- `exporting` → formatter running
- `completed` → artifacts created

Failure / stop states:
- `failed` → unrecoverable error
- `cancelled` → manually cancelled

**Allowed transitions** (simplified):
- `created` → `planning`
- `planning` → `generating` | `failed`
- `generating` → `awaiting_review` | `ready_to_export` | `failed`
- `awaiting_review` → `generating` | `ready_to_export` | `cancelled`
- `ready_to_export` → `exporting`
- `exporting` → `completed` | `failed`

### 2.2 Run Item Statuses
Use item-level states so retries and teacher actions are explicit:

- `planned` → slot created
- `retrieving` → Retriever tool call in progress
- `retrieved` → context pack ready
- `drafting` → LLM generation in progress
- `drafted` → draft produced
- `evaluating` → Evaluation tool in progress
- `needs_regen` → failed evaluation and regen is available
- `regenerating` → single regen attempt
- `needs_review` → delivered to teacher (either pass or fail after regen)
- `approved` → teacher approved
- `edited` → teacher edited and approved
- `rejected` → teacher rejected

Terminal/stop:
- `blocked` → cannot proceed automatically (e.g., missing evidence)
- `failed` → system failure for item

**Policy**: export gating treats `approved` and `edited` as acceptable, but not `rejected`.

---

## 3) Retry & Idempotency

### 3.1 Regeneration policy (hard rule)
- Maximum regeneration attempts per item: **1**
- Trigger: `faithfulness < threshold` or `relevancy < threshold`
- After regen:
  - If pass → `needs_review`
  - If fail again → `needs_review` with `evaluation.failures` populated

### 3.2 Tool-call retries (infrastructure)
- MCP tool calls may be retried on transient errors (timeouts, 5xx)
- Retries must be **idempotent**.

### 3.3 Idempotency keys
All orchestrator writes should be safe under retry:
- `POST /runs` uses `Idempotency-Key` header
- Item processing uses deterministic keys, e.g. `run_id + item_id + step_name`

---

## 4) Workflow: Phase 1 Generation

### 4.1 Planning
1. Resolve scope (Syllabus Tool)
2. Expand blueprint into N slots (`run_items`)
3. Set run status → `generating`

### 4.2 Per-item execution
For each item (parallelizable with worker pool limits):
1. `retrieving` → call Retriever Tool → `retrieved`
2. `drafting` → call LLM → `drafted`
3. `evaluating` → call Evaluation Tool
   - pass → `needs_review`
   - fail → `needs_regen`
4. If `needs_regen` and attempts remaining:
   - `regenerating` → call LLM regen → `drafted` → `evaluating`
5. Persist final item in `needs_review`.

### 4.3 Teacher review
Teacher actions:
- Approve → item `approved`
- Edit → item `edited` (store final text + audit)
- Reject → item `rejected` (requires replacement flow: regenerate/new slot)
- Request Regenerate → item returns to `regenerating` (only if policy allows; recommended: **1 manual regen** separate from auto regen)

### 4.4 Export
When all required slots are `approved|edited`:
- run status → `ready_to_export`
- call Formatter Tool → `exporting` → `completed`

---

## 5) Event Log

### 5.1 Why events
- Rebuild run state from events (audit)
- Debug failures and measure ROI
- Feed analytics and learning loop

### 5.2 Event schema
```json
{
  "event_id": "uuid",
  "run_id": "uuid",
  "item_id": "uuid|null",
  "type": "RUN_CREATED|SCOPE_RESOLVED|ITEM_RETRIEVED|ITEM_DRAFTED|ITEM_EVALUATED|ITEM_REGEN_REQUESTED|ITEM_REGENERATED|TEACHER_APPROVED|TEACHER_EDITED|TEACHER_REJECTED|EXPORT_STARTED|EXPORT_COMPLETED|RUN_FAILED",
  "ts": "2026-01-13T10:00:00Z",
  "actor": {"type": "service|teacher", "id": "..."},
  "data": {}
}
```

### 5.3 Minimal events to implement first
- `RUN_CREATED`, `SCOPE_RESOLVED`, `ITEM_RETRIEVED`, `ITEM_DRAFTED`, `ITEM_EVALUATED`
- `TEACHER_APPROVED`, `TEACHER_EDITED`, `TEACHER_REJECTED`
- `EXPORT_STARTED`, `EXPORT_COMPLETED`, `RUN_FAILED`

---

## 6) Data Persistence Notes

### 6.1 Strongly recommended
- Store the exact `context_pack` used for each draft (or a hash + chunk ids)
- Store model identifiers + prompt versions per draft
- Store evaluation thresholds used at the time of scoring

### 6.2 PII boundaries
Phase 1/2 has no student PII. Phase 3 must separate/lock down student artifacts and redact traces.

---

## 7) Learning loop (teacher feedback → better outputs)

Teacher review is not only an approval gate; it is also the primary signal for continuous improvement.

### 7.1 Signals captured
- `TEACHER_APPROVED`: positive signal (keep as exemplar candidate)
- `TEACHER_EDITED`: strong signal (store draft vs final diff + rationale)
- `TEACHER_REJECTED`: negative signal (require categorized reason)

### 7.2 Outputs of the learning loop
1. Few-shot exemplars
  - Curate approved/edited items into an `exemplars` store by scope + slot features
  - During drafting, retrieve top-K exemplars and inject them as few-shot examples
2. Prompt template iteration
  - Maintain versioned `prompt_templates` per subject/slot kind
  - Update templates based on frequent edit patterns and rejection categories
3. Retrieval improvements
  - Update `retrieval_policies` (query templates, RRF parameters, context-pack rules)
  - Use “evidence sufficiency” and teacher edits to detect missing/weak context

### 7.3 Governance
- Changes are versioned and auditable (template version, exemplar set, retrieval policy)
- Evaluate changes against the gold dataset before rollout
- Fine-tuning is optional and requires explicit opt-in + compliance checks
