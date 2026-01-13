# Risks & Mitigations

## Key risks
- PDF quality variability
  - Mitigation: PDF classification + layout/OCR pipeline; book-specific extraction profiles.
- Teacher trust
  - Mitigation: mandatory HITL; evidence always visible.
- Hallucinations
  - Mitigation: strict evidence rules + DeepEval + rejection feedback.
- Cost creep
  - Mitigation: provider abstraction + caching + telemetry + per-run budgets.
- Compliance (Phase 3)
  - Mitigation: privacy-by-design for student records (GDPR/local data protection), strict retention/deletion, data residency controls where required, PII redaction in logs/traces, and auditable access logs.

## Implementation Checklist (build first)
1. Data ingestion for one subject slice + smart chunk schema
2. Hybrid retrieval + RRF + context pack builder
3. Orchestrator generation workflow + evaluation loop
4. Teacher portal review/edit/export
5. Gold dataset + benchmark harness + KPI dashboard
