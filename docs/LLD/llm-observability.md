# LLD — LLM Adapters & Observability

## 1. LLM Adapter Design
Goal: allow per-run provider/model selection without changing orchestration logic.

Key types:
- LLMRequest: messages + provider + model + decoding params
- LLMResponse: text + raw + optional usage fields

Factory:
- services/orchestrator/app/llm/factory.py

Providers:
- mock: deterministic JSON output for dev
- openai: Responses API
- anthropic: Messages API
- groq: OpenAI-compatible chat completions

Usage extraction (current):
- OpenAI: usage.input_tokens/output_tokens/total_tokens
- Groq: usage.prompt_tokens/completion_tokens/total_tokens
- Anthropic: usage.input_tokens/output_tokens (total computed)

Cost calculation:
- cost_usd is currently optional and not computed by default.
- The worker tracks cost_usd.known to avoid reporting misleading $0 values.

## 2. Worker Spans (Tracing)
Worker creates spans:
- run.process
- item.process
- item.retrieve
- item.draft.llm
- item.evaluate

Span attributes include:
- run.id, tenant.id
- item.id, slot metadata
- llm.provider, llm.model
- llm usage (tokens) when available

## 3. OpenTelemetry Bootstrap
- services/orchestrator/app/observability.py
  - init_otel(app, enabled, service_name, otlp_endpoint, console_exporter, sample_rate)
  - Instruments FastAPI + httpx

Config:
- OBSERVABILITY_ENABLED
- OTEL_SERVICE_NAME
- OTEL_EXPORTER_OTLP_ENDPOINT (OTLP/HTTP traces endpoint; e.g., http://localhost:4318/v1/traces)
- OTEL_EXPORTER_CONSOLE
- OTEL_SAMPLE_RATE

## 4. Run Metrics Aggregation
Worker maintains run.metrics:
- latency_ms per phase
- tokens totals
- cost_usd totals (if known)

Persistence:
- repo.update_run_metrics emits RUN_METRICS_UPDATED event for auditability.

## 5. Future Enhancements
- Pricing tables per provider/model to compute cost_usd deterministically
- Propagate trace context across background jobs / distributed workers
- Add PII redaction filters for logs/traces (Phase 3 requirement)
