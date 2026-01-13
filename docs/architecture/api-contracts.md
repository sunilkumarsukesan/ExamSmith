# API Contracts

This section describes the orchestrator-facing API surface for the Teacher Portal and the high-level MCP tool contracts.

## Orchestrator APIs (Teacher workflows)
- `POST /blueprints` create/update
- `POST /runs` start generation from a blueprint
- `GET /runs/{run_id}` status + progress
- `GET /runs/{run_id}/items` list review items
- `POST /runs/{run_id}/items/{item_id}/approve|edit|reject|regenerate`
- `POST /runs/{run_id}/export` export DOCX/PDF

## MCP Tool Interfaces (high-level)
The orchestrator is the only MCP client.

### Syllabus Tool
- Validate scope: (board, standard, subject, chapter/topic)
- Map blueprint slots → eligible chapters/topics

### Retriever Tool
- Hybrid search (vector + keyword) + RRF
- Context pack builder enforcing evidence rules

### Diagram Tool
- Fetch diagram assets referenced by retrieved chunks
- Optionally transform for export (resize, format conversion)

### Formatter Tool
- Produce DOCX/PDF
- Insert citations and diagrams
- Render LaTeX consistently

### Evaluation Tool
- DeepEval checks (faithfulness, relevancy)
- Return scores + failure reasons

### Analytics Tool
- Token/cost attribution per run
- KPI computation (time saved, approval rates, regen rates)

## RunConfig (LLM selection)

`POST /runs` supports per-run LLM selection via the optional `config` object:
- `config.llm_provider`
- `config.llm_model`
- `config.temperature`
- `config.top_p`
- `config.max_output_tokens`

If omitted, the orchestrator uses environment defaults.
