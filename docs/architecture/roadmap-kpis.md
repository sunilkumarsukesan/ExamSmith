# Roadmap & KPIs

## Phase 0 — Closed Pilot (4–6 weeks)
Goal: validate teacher workflow + ROI assumptions with a single school/teacher group.

Delivery milestones:
- Pilot agreement in place (1 school; 5–15 teachers) with named stakeholders
- Pilot onboarding complete (RBAC, tenant setup, basic audit logging)
- Teacher Portal MVP usable end-to-end (create run → review → export)
- Curriculum ingest MVP complete for a narrow slice (e.g., one grade + one subject)
- Gold dataset + benchmark harness established (minimum viable evaluation set)
- Pricing hypothesis validated with pilot (e.g., credit-based subscription assumptions)

KPIs (measured on pilot baseline and tracked weekly):
- ≥ 30% reduction in end-to-end time for teachers to create a blueprint-aligned paper (baseline measured pre-pilot)
- ≥ 70% item approval rate after edits (approved+edited / total)
- ≥ 80% of runs reach export (export success rate)
- Cost-per-approved-paper (₹) within target band (define per-tenant budget in pilot agreement)

Exit criteria (Go/No-Go):
- At least 10 exported papers generated during pilot
- At least 3 teachers use the system weekly
- No critical policy violations (source policy, privacy boundaries)

## Phase 1 — Blueprint-aligned paper generation (6–10 weeks)
Goal: production-grade generation + citations.
- Strict/Free blueprints
- Hybrid retrieval + RRF
- Evaluation loop + guardrails

Delivery milestones:
- Blueprint authoring UX hardened (templates, reuse, validation)
- Evidence/citation format standardized (page refs + snippet IDs)
- Reliability improvements (idempotent processing, retry strategy, basic rate-limit handling)

KPIs:
- ≥ 60% reduction in teacher time to create a blueprint-aligned paper (measured vs Phase 0 baseline)
- Faithfulness pass rate ≥ 85% on first attempt (guardrail metric)
- Regen rate ≤ 25% (items regenerated / total items)
- P95 time-to-first-draft per item ≤ target threshold (set per pilot hardware/provider)

## Phase 2 — Answer keys & marking schemes (6–8 weeks)
Goal: reduce teacher workload in solution drafting.
- Structured marking scheme generation
- Rubric templates per subject

KPIs:
- ≥ 50% reduction in teacher time to create answer keys/marking schemes
- Teacher edit rate trending downward month-over-month
- Rejection reasons shift from "content wrong" → "styling/preferences" (quality trend)

## Phase 3 — Scanned answer evaluation (8–12+ weeks)
Goal: reliable ingestion and grading with compliance.
- OCR/handwriting engine integration (specialized OCR/vision tooling such as AWS Textract or Azure AI Document Intelligence; standard LLMs are not reliable for handwritten OCR)
- Grading rubrics + auditability
- KPIs:
  - Agreement with teachers ≥ target threshold on pilot dataset
  - Student-record privacy compliance checks passing (GDPR/local data protection), including retention/deletion and access auditability

## Phase 4 — Learning modules & quizzes
Goal: student-facing engagement.
