# LLD — Orchestrator API

Base URLs:
- /runs
- /blueprints

## 1. Blueprints
### POST /blueprints
Creates or upserts a blueprint.
- Input: tenant_id, board, standard, subject, total_marks, sections[]
- Output: blueprint

### GET /blueprints?tenant_id=...
Lists blueprints for a tenant.

### GET /blueprints/{blueprint_id}?tenant_id=...
Fetches one blueprint.

## 2. Runs
### POST /runs
Creates a run.
- Input: tenant_id, scope, mode, (blueprint_id OR slots[]), optional config
- Behavior:
  - If blueprint_id is provided and slots omitted, backend expands blueprint into slots.
  - Applies default RunConfig (including LLM defaults) when fields are missing.
  - If auto processing enabled, enqueues background processing.
- Output: run + items

### POST /runs/{run_id}/process
Queues processing for an existing run.

### GET /runs/{run_id}
Returns run state (status, config, metrics).

### GET /runs/{run_id}/items
Returns items for the run.

### GET /runs/{run_id}/events
Returns append-only events for the run.

### POST /runs/{run_id}/items/{item_id}/action
Teacher actions:
- approve
- edit (requires final_question_text + final_answer_key)
- reject
- regenerate (currently changes status; full regen policy to be implemented)

### POST /runs/{run_id}/export
Export gating:
- Allowed only if all items are approved/edited.
- Current implementation returns stub artifacts; formatter integration is planned.

## 3. Error semantics (current)
- 404 for missing run/item/blueprint
- 409 for export when run not ready
- 400 for invalid combinations (e.g., blueprint_id + slots)
