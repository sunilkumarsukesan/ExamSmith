
# ExamSmith — Architecture

**Document status:** Living architecture baseline for implementation (Jan 13, 2026)

This file is the entry point. The detailed, build-ready architecture is split into subsystem docs under `docs/architecture/`.

## Quick links
- docs/architecture/README.md

## Reading order (recommended)
1. docs/architecture/system-overview.md
2. docs/architecture/ingestion.md
3. docs/architecture/retrieval.md
4. docs/architecture/generation.md
5. docs/architecture/hitl-feedback.md
6. docs/architecture/orchestrator-workflows.md
7. docs/architecture/data-model.md
8. docs/architecture/api-contracts.md
9. docs/architecture/mcp-tool-specs.md
10. docs/architecture/security-compliance.md
11. docs/architecture/observability-roi.md
12. docs/architecture/deployment-scaling.md
13. docs/architecture/roadmap-kpis.md
14. docs/architecture/risks.md

## One-page summary
ExamSmith is a curriculum-locked RAG platform for Tamil Nadu (Samacheer Kalvi) and CBSE that generates blueprint-aligned assessments by reasoning strictly over official textbooks and approved curriculum blueprints.

Key pillars:
- Curriculum-aware ingestion into MongoDB Atlas (vectors + keyword search)
- Hybrid retrieval (vector + keyword) combined via RRF
- Evidence-first generation with automated evaluation (DeepEval) as a guardrail (not a release gate)
- Mandatory teacher HITL review UI before export (approve/edit/reject), since exams are high-stakes
- Observability for quality, latency, and cost-per-paper ROI
- Feedback loop: teacher edits/rejections are stored and used to improve future runs (few-shot exemplar library, prompt template versioning, retrieval/query-template tuning; optional fine-tuning later with opt-in/compliance)

Phase 3 (future): scanned answer sheet evaluation requires a specialized OCR/vision engine (e.g., AWS Textract or Azure AI Document Intelligence) to handle handwritten text; standard LLMs alone are not reliable for handwriting OCR.

Phase 3 (future): scanned student answer sheets introduce student-record privacy obligations (GDPR/local data protection laws). Architecture must enforce privacy-by-design (data minimization, retention/deletion, RBAC, encryption, audit logs, regional data residency where required, and PII redaction in logs/traces).

