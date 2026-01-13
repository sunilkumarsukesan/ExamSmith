# LLD — Storage Layer

## 1. Repository Pattern
The Orchestrator depends on RunRepository (interface) with two implementations:
- InMemoryRunRepository (dev)
- MongoRunRepository (production)

Interface location:
- services/orchestrator/app/storage/repo.py

## 2. Storage Responsibilities
- Persist runs and items
- Persist blueprints
- Append events to an event log
- Enforce export gating rules via run/item status updates
- Persist run metrics patches (latency/tokens/cost) via update_run_metrics

## 3. In-memory Backend
- Dict-based storage keyed by UUID
- Blueprint expansion into slots performed in create_run
- Event storage is per-run list

## 4. Mongo Backend
Collections:
- generation_runs
- run_items
- run_events
- blueprints

Notes:
- Uses Motor async client
- Identifiers are stored as strings in Mongo (UUIDs serialized)
- update_run_metrics uses shallow merge semantics:
  - In Mongo: metrics.<key> is set per patch key

## 5. Consistency and Concurrency
Current behavior is simple and suitable for MVP:
- Item actions update item + append event
- Run gating status recalculated from current items

Future improvements:
- Add optimistic concurrency control (updated_at checks)
- Add idempotency keys for create_run and item actions
- Consider event-sourcing rebuild as a recovery path

## 6. Metrics
update_run_metrics(run_id, metrics_patch, actor, data)
- Applies a patch into run.metrics
- Emits RUN_METRICS_UPDATED event (if provided)

Metrics shape (current):
- latency_ms: {retrieval, llm, evaluation, total}
- tokens: {input, output, total}
- cost_usd: {known, total}
- items: {count}
- llm: {provider, model}
