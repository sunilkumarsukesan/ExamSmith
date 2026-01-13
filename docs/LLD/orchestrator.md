# LLD — Orchestrator Service

## 1. Purpose
The Orchestrator is the workflow engine for question-paper generation runs. It:
- Owns run/item lifecycle state transitions.
- Emits an append-only event log for auditability.
- Integrates LLM providers via a thin adapter layer.
- Provides a REST API used by the Teacher Portal.

## 2. Module Structure
- app/main.py
  - FastAPI app initialization
  - CORS middleware
  - Router mounting
  - OpenTelemetry bootstrap
- app/models.py
  - Pydantic models: GenerationRun, RunItem, Blueprint, RunEvent, configs
  - Enums: RunStatus, ItemStatus, EventType
- app/api/
  - runs.py: run creation, processing, item actions, export, events
  - blueprints.py: blueprint CRUD
  - router.py: registers routers
- app/workers/generation.py
  - process_run: stubbed pipeline for retrieve → draft → evaluate
  - Writes events and metrics
- app/storage/
  - repo.py: repository interface
  - inmemory.py: dev backend
  - mongo.py: Motor backend
- app/llm/
  - types.py: request/response shapes
  - factory.py: selects provider
  - openai.py / anthropic.py / groq.py / mock.py

## 3. State Machine
### 3.1 Run statuses
- created → planning → generating → awaiting_review → ready_to_export → exporting → completed
- failed / cancelled terminal states

### 3.2 Item statuses
- planned → retrieving → retrieved → drafting → drafted → evaluating → needs_review
- teacher actions: approved / edited / rejected

Export gating rule:
- export allowed only when every item is approved or edited.

### 3.3 Diagram — State Machine (Run + Item)
![LLD — State Machine (Run + Item)](<../assets/diagrams/lld/LLD — State Machine (Run + Item).png>)

## 4. Events (Audit Log)
RunEvent fields:
- event_id, run_id, item_id (optional)
- type (EventType)
- ts
- actor {type, id}
- data {arbitrary dict}

Important event types:
- RUN_CREATED
- ITEM_RETRIEVED / ITEM_DRAFTED / ITEM_EVALUATED
- TEACHER_APPROVED / TEACHER_EDITED / TEACHER_REJECTED
- EXPORT_STARTED / EXPORT_COMPLETED
- RUN_METRICS_UPDATED (run-level telemetry patch)

## 5. Processing Model
### 5.1 Triggering processing
- Automatic (if AUTO_PROCESS_RUNS=true) via FastAPI BackgroundTasks on POST /runs
- Manual: POST /runs/{run_id}/process

### 5.2 Current worker behavior (stub)
Per item:
- Retrieval: currently stubbed chunk list
- Drafting: calls selected LLM provider (mock/openai/anthropic/groq)
- Evaluation: currently stubbed scores
- Final: item set to needs_review

### 5.3 Future direction
Replace stubs with MCP tool calls:
- Retriever Tool for hybrid retrieval/context packing
- Evaluation Tool for DeepEval + policy checks
- Formatter Tool for DOCX/PDF export

### 5.4 Diagram — Sequence (Create Run → Process → Review → Export)
![LLD — Sequence Diagram Create Run → Process → Review → Export](<../assets/diagrams/lld/LLD — Sequence Diagram Create Run → Process → Review → Export.png>)

## 6. LLM Selection
RunConfig supports per-run selection:
- llm_provider, llm_model
- temperature, top_p, max_output_tokens

Defaults are applied server-side when missing.

## 7. Non-functional Requirements
- Idempotency: planned; event log supports reconstruction.
- Observability: OpenTelemetry spans around phases.
- Security: Phase 1/2 no student PII; Phase 3 must enforce student privacy boundaries.
