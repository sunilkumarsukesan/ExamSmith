# Roadmap & KPIs

## Phase 0 — Closed Pilot (4–6 weeks)
Goal: validate teacher workflow + ROI assumptions with a single school/teacher group.
- Deliver teacher portal (review/edit/export)
- Ingest MVP slice textbooks
- Establish gold dataset and benchmark harness
- KPIs:
  - ≥ 30% time reduction vs manual paper creation (pilot baseline)
  - ≥ 70% teacher approval rate after edits
  - Cost-per-paper within target band

## Phase 1 — Blueprint-aligned paper generation (6–10 weeks)
Goal: production-grade generation + citations.
- Strict/Free blueprints
- Hybrid retrieval + RRF
- Evaluation loop + guardrails
- KPIs:
  - ≥ 60% time reduction
  - Faithfulness pass rate ≥ 85% first attempt
  - Regen rate ≤ 25%

## Phase 2 — Answer keys & marking schemes (6–8 weeks)
Goal: reduce teacher workload in solution drafting.
- Structured marking scheme generation
- Rubric templates per subject
- KPIs:
  - ≥ 50% reduction in time to create answer keys
  - Teacher edit rate trending downward month-over-month

## Phase 3 — Scanned answer evaluation (8–12+ weeks)
Goal: reliable ingestion and grading with compliance.
- OCR/handwriting engine integration (specialized OCR/vision tooling such as AWS Textract or Azure AI Document Intelligence; standard LLMs are not reliable for handwritten OCR)
- Grading rubrics + auditability
- KPIs:
  - Agreement with teachers ≥ target threshold on pilot dataset
  - Student-record privacy compliance checks passing (GDPR/local data protection), including retention/deletion and access auditability

## Phase 4 — Learning modules & quizzes
Goal: student-facing engagement.
