# ExamSmith Orchestrator (FastAPI)

This service implements the Orchestrator API and the deterministic run/item workflow model described in:
- ../../docs/architecture/orchestrator-workflows.md
- ../../docs/architecture/mcp-tool-specs.md

## Run locally

1. Create a virtualenv and install deps
- `python -m venv .venv`
- `./.venv/Scripts/pip install -r requirements.txt`

2. Configure env
- Copy `.env.example` to `.env` and adjust as needed.

3. Start the API
- `./.venv/Scripts/uvicorn app.main:app --reload --port 8000`

Open:
- http://localhost:8000/docs

## Storage backends
- `STORAGE_BACKEND=inmemory` (default): no external dependencies
- `STORAGE_BACKEND=mongo`: persists runs/items/events in MongoDB (Motor)

## What’s implemented
- Core REST endpoints for runs and item review actions
- Run + item status enums, transition validation (basic)
- Append-only event log
- Blueprint CRUD + expansion into run slots

## Auto-processing (stub worker)

The repo includes a stub run processor that simulates retrieve → draft → evaluate transitions.

- Set `AUTO_PROCESS_RUNS=true` to enqueue processing automatically on `POST /runs`.
- Or manually enqueue for an existing run via `POST /runs/{run_id}/process`.
- Watch progress via `GET /runs/{run_id}/events`.

## LLM selection (per run)

You can select which LLM to use per run via `CreateRunRequest.config`:
- `llm_provider`: `mock` | `openai` | `anthropic` | `groq` (more providers can be added)
- `llm_model`: model name for the provider
- `temperature`, `top_p`, `max_output_tokens`

If you omit these, environment defaults are used (`DEFAULT_LLM_*`). For local dev without API keys, set `DEFAULT_LLM_PROVIDER=mock`.

Provider keys (only needed for real providers):
- `OPENAI_API_KEY` (optionally `OPENAI_BASE_URL`)
- `ANTHROPIC_API_KEY` (optionally `ANTHROPIC_BASE_URL`, `ANTHROPIC_VERSION`)
- `GROQ_API_KEY` (optionally `GROQ_BASE_URL`)

## Blueprints (MVP)

- Create: `POST /blueprints`
- List: `GET /blueprints?tenant_id=...`
- Get: `GET /blueprints/{blueprint_id}?tenant_id=...`

To create a run from a stored blueprint, call `POST /runs` with `blueprint_id` and omit `slots`.

## What’s next
- MCP tool invocation wiring (syllabus → retrieval → evaluation → formatter)
- Worker queue for parallel item generation
