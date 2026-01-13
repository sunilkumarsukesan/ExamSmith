# ExamSmith — High-Level Design (HLD)

**Status:** Draft for team collaboration (Jan 2026)

## 1. Objective
ExamSmith is a curriculum-locked assessment generation platform for TN (Samacheer Kalvi) + CBSE.

Primary outcomes:
- Generate blueprint-aligned question papers from official textbooks only (no open web).
- Provide evidence/citations per question.
- Enforce Human-in-the-Loop (HITL): teacher review/edit/reject before export.
- Provide observability and ROI metrics (latency/tokens/cost-per-paper).

Non-goals (Phase 1/2):
- Autonomous high-stakes publishing without teacher approval.
- Student answer sheet evaluation.

## 2. Scope by Phase
### Phase 0/1 (current build)
- Ingest textbooks → chunk + index (vector + keyword).
- Blueprint CRUD and blueprint-driven run creation.
- Orchestrator workflow: retrieve → draft → evaluate → needs_review.
- Teacher Portal workflows (approve/edit/reject; export gating).

### Phase 2
- Answer keys / marking schemes; rubric templates.

### Phase 3 (future)
- Scanned student answer sheets:
  - Handwriting-capable OCR/vision engine required (e.g., AWS Textract or Azure AI Document Intelligence).
  - Student-record privacy controls by design (GDPR/local data protection laws, DPAs, retention/deletion, auditability).

## 3. System Context (Actors and Systems)
Actors:
- Teacher/Reviewer: creates runs, reviews items, approves/edits/rejects, exports papers.
- Admin/Ops: tenant/user management, monitoring, compliance oversight.

External/adjacent systems:
- LLM providers (OpenAI / Anthropic / Groq; future: Azure OpenAI/local).
- MongoDB Atlas (data store + vector + keyword search).
- Object storage (S3/Azure Blob): PDFs, diagrams, exports.
- Observability backends (OTLP collector, Arize Phoenix, etc.).

### 3.1 Diagram — System Context (C4-L1)
![HLD — System Context (C4-L1)](<assets/diagrams/hld/HLD — System Context (C4-L1).png>)

## 4. High-Level Architecture
### 4.1 Component Diagram (conceptual)
- Teacher Portal (UI)
  - Calls Orchestrator API
- Orchestrator (FastAPI)
  - Run lifecycle + workflow engine
  - Calls MCP tools + LLM provider adapters
  - Persists events and state
- MCP Tool Layer (future)
  - Syllabus Tool
  - Retriever Tool
  - Diagram Tool
  - Formatter Tool
  - Evaluation Tool
- Storage
  - MongoDB Atlas collections: runs, items, events, blueprints
  - Object storage for artifacts

### 4.2 Diagram — Container Diagram (C4-L2)
![HLD — Container Diagram (C4-L2)](<assets/diagrams/hld/HLD — Container Diagram (C4-L2).png>)

### 4.3 Data Flow (Phase 1)
1. Teacher creates blueprint
2. Teacher creates run (by blueprint_id)
3. Orchestrator expands blueprint into item slots
4. Worker processes items:
   - retrieval (context pack)
   - LLM drafting
   - evaluation (DeepEval)
   - item → needs_review
5. Teacher reviews in UI:
   - approve/edit/reject/regenerate
6. Export is enabled only if all required items are approved/edited

## 5. Key Design Principles
- Curriculum lock: only official sources, scoped by board/standard/subject/chapter/topic.
- Deterministic workflow: explicit run/item statuses; append-only event log.
- Evidence-first outputs: enforce citations + page refs.
- Human authority: teacher approval is the release gate; DeepEval is a guardrail.
- Observability-first: measure latency/tokens/cost at run level.
- Tenant isolation: school/tenant boundaries for data segregation.

## 6. Storage Model (High Level)
Primary entities:
- Blueprint: templates → slot expansion
- GenerationRun: one end-to-end execution
- RunItem: one slot/question
- RunEvent: append-only audit log

Backends:
- In-memory backend for dev
- Mongo backend for persistence/production

## 7. Reliability and Scaling (High Level)
- Background processing for runs (queue-based later; currently FastAPI background tasks).
- Idempotency and event-sourcing patterns (append-only events).
- Future: worker pool / queue (Celery/Redis, SQS, etc.) for parallel processing.

## 8. Security, Privacy, Compliance (High Level)
- RBAC: Teacher/Admin/Reviewer/Ops
- Tenant isolation
- Encryption in transit + at rest
- Audit logs for teacher actions and exports

Phase 3 compliance additions:
- Student answer sheets treated as sensitive student records (GDPR/local data protection).
- Retention/deletion controls; avoid PII in logs/traces.
- Vendor governance for OCR/vision providers.

## 9. Observability & ROI (High Level)
- Tracing: OpenTelemetry for API + worker phases + outbound calls.
- Run metrics: tokens, latency per phase, cost-per-paper (pricing model to be added).
- Dashboards: quality pass rate, regen rate, teacher edit rate, cost-per-paper.

## 10. Collaboration Plan (Suggested Workstreams)
- Frontend: Teacher Portal (run list, item review UI, export)
- Retrieval: hybrid retrieval + context pack builder (MCP tool)
- Evaluation: DeepEval integration + failure taxonomy
- Formatting: DOCX/PDF formatter tool
- Observability: OTLP export + dashboards + pricing-based cost model
- Phase 3 prep: OCR pipeline design + student privacy boundaries

## 11. References
- Architecture entry point: ../Architecture.md
- Architecture subsystem docs: architecture/
- Orchestrator code: ../services/orchestrator/
