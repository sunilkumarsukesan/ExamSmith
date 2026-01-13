# ExamSmith — Low-Level Design (LLD)

This folder contains implementation-oriented low-level designs mapped to the current codebase.

## Reading order
1. orchestrator.md
2. api.md
3. storage.md
4. llm-observability.md

## Diagrams
- The state machine and sequence diagrams are embedded in orchestrator.md.

## Code map
- FastAPI app: services/orchestrator/app/main.py
- Domain models: services/orchestrator/app/models.py
- Settings/env: services/orchestrator/app/settings.py and services/orchestrator/.env.example
- API routers: services/orchestrator/app/api/
- Worker: services/orchestrator/app/workers/generation.py
- Storage backends: services/orchestrator/app/storage/
- LLM adapters: services/orchestrator/app/llm/
- OpenTelemetry bootstrap: services/orchestrator/app/observability.py
