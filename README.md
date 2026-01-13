# ExamSmith

ExamSmith is a curriculum-locked assessment generation platform (TN Samacheer Kalvi + CBSE) with strict Human-in-the-Loop (HITL) teacher review before export.

- Source policy: official textbooks only (no open web)
- Workflow: deterministic run/item state machine with append-only event log
- LLM: per-run provider/model selection (mock/OpenAI/Anthropic/Groq)
- Observability: OpenTelemetry traces + run-level ROI metrics (latency/tokens/cost hooks)

## Repository layout
- [Architecture.md](Architecture.md): architecture entry point
- [docs/HLD.md](docs/HLD.md): High-Level Design (includes diagrams)
- [docs/LLD/README.md](docs/LLD/README.md): Low-Level Design index
- services/
  - services/orchestrator/: FastAPI Orchestrator service (runnable)

Diagrams are stored under [docs/assets/diagrams/](docs/assets/diagrams/).

## Quickstart (Orchestrator API)

From the repo root:

```powershell
cd services/orchestrator
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Open Swagger UI:
- http://localhost:8000/docs

### Storage backends
- `STORAGE_BACKEND=inmemory` (default): no external dependencies
- `STORAGE_BACKEND=mongo`: persists runs/items/events in MongoDB (Motor)

### LLM selection (per run)
You can set defaults in `services/orchestrator/.env`:
- `DEFAULT_LLM_PROVIDER=mock|openai|anthropic|groq`
- `DEFAULT_LLM_MODEL=...`

Or override per run via the create-run request config.

## Docs
- Architecture subsystem docs: [docs/architecture/README.md](docs/architecture/README.md)
- Orchestrator service docs: [services/orchestrator/README.md](services/orchestrator/README.md)

## Current status
Implemented today:
- Blueprint CRUD + blueprint-driven run creation
- Run processing stub (retrieve → draft → evaluate → needs_review)
- Teacher actions (approve/edit/reject) + export gating
- Event log + basic observability plumbing

Planned next:
- MCP tool wiring for retrieval/evaluation/formatter
- Teacher Portal UI
- Phase 3: handwriting OCR + student privacy boundary controls
