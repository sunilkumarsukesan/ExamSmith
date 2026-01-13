# Deployment & Scaling

## Runtime
- Containerized services (Docker)
- Deployment: AWS ECS/EKS or Azure AKS (choose one for MVP)
- Environments: dev/stage/prod

## Scaling approach
- Horizontal scale orchestrator workers by run queue length
- Cache syllabus and blueprint templates in Redis
- Precompute embeddings during ingestion; avoid on-demand embedding spikes

## Reliability
- Idempotent workflow steps (safe retries)
- Timeouts/circuit breakers for external LLM/OCR providers
- Dead-letter queue for failed runs + manual triage
