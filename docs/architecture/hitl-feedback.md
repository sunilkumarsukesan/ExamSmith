# Human-in-the-Loop (HITL) & Feedback Loop

## Why HITL is mandatory
Even with automated evaluation, an exam system must include a teacher review/edit step before final export to protect against ambiguity, poor phrasing, and context edge cases.

**High-stakes policy**: DeepEval (e.g., a faithfulness score > 0.85) is a helpful guardrail, but it is not sufficient on its own in an educational context. Final export must be gated on explicit teacher approval (approve/edit/reject) through a dedicated review UI.

## Teacher Portal requirements (Phase 0/1)
- Review list per generation run
- For each question:
  - show question, answer key, marks, difficulty, taxonomy tags
  - show evidence excerpts + page refs + diagram previews
  - actions: Approve / Edit / Reject / Request Regenerate
- Export is enabled only when all required slots are approved.

## What gets logged (for audit + learning)
- Original model output
- Teacher edited final text
- Rejection reason (categorized)
- Evidence sufficiency flags
- Time spent per item (for ROI)

## Feedback Loop (Learning System)
Teacher feedback should improve outcomes without requiring immediate fine-tuning.

### How corrections feed back (mechanics)
Teacher actions create structured training signals:
- `approved` → positive exemplar
- `edited` → strongest exemplar (diff between draft and final highlights prompt gaps)
- `rejected` → negative signal (categorize reason)

The system uses these signals to update three things over time:
1. Few-shot exemplars (prompt-time)
  - Maintain an `exemplars` store keyed by scope (board/standard/subject/chapter/topic) + slot features (marks/difficulty/taxonomy)
  - At generation time, retrieve top-K exemplars and include them as few-shot examples (with strict evidence requirements)
2. Prompt templates (prompt-engineering)
  - Version prompt templates per subject/slot type
  - Use rejection categories and edit diffs to refine instructions (format, common mistakes, required phrasing)
3. Retrieval/query templates (RAG quality)
  - If teachers frequently edit for missing definitions/evidence, adjust retrieval query templates and context-pack rules
  - Track which chunk IDs were cited and whether they were sufficient to support the final teacher-approved answer

### Short-term (no training)
- Store edited/approved items as exemplars for few-shot prompts by scope
- Update retrieval weighting and query templates based on failure categories
- Maintain a per-subject banned-pattern list (common hallucination traps)

### Medium-term
- Preference models / rerank rules driven by approval data
- Lightweight “likely rejection” classifier to reduce teacher load

### Long-term (optional)
- Fine-tuning/adapters using approved + edited items (only if licensing/compliance allows)

If fine-tuning is introduced:
- Use only teacher-approved data (never raw rejects without review)
- Require explicit tenant opt-in + retention rules
- Keep a rollback plan (model versioning + A/B evaluation on the gold set)
