# System Overview

## Purpose
ExamSmith is a curriculum-locked RAG platform for Tamil Nadu (Samacheer Kalvi) and CBSE that generates blueprint-aligned assessments by reasoning strictly over official textbooks and approved curriculum blueprints.

ExamSmith integrates Model Context Protocol (MCP) to decouple the core LLM from specialized data/tools (syllabus mapping, retrieval, diagrams, formatting, evaluation), enabling plug-and-play architecture and gradual scaling.

## Scope
### In scope (MVP → Phase 2)
- Ingest official PDFs into a curriculum-aware knowledge base with vectors + keyword indexes.
- Blueprint-driven question paper generation (Strict/Free modes).
- Evidence/citations on every generated question.
- Human-in-the-loop (teacher review/edit/reject) before export.
- Export to DOCX/PDF with LaTeX math and diagrams.
- Automated evaluation (faithfulness/relevancy) with controlled regeneration.
- Question bank persistence with metadata, evaluation scores, and teacher feedback.
	- Feedback loop: teacher edits/rejections drive exemplar (few-shot) libraries, prompt template iteration, and retrieval/query-template tuning (optional fine-tuning later with opt-in/compliance).

### Future scope (Phase 3+)
- Evaluation of scanned student answer sheets (OCR/vision + semantic grading). This requires a handwriting-capable OCR engine (e.g., AWS Textract or Azure AI Document Intelligence); LLMs are not a substitute for OCR on handwritten work. It also requires student-record privacy controls (GDPR/local data protection laws) by design.
- Interactive quizzes and learning modules.

### Non-goals
- Using general web sources for question generation.
- Autonomous publication of high-stakes papers without teacher sign-off.

## Product Principles & Guardrails
1. Curriculum lock: every output maps to (board, standard, subject, chapter/topic).
2. Evidence-first generation: questions must meet minimum evidence rules.
3. Human authority: teacher approval required for final export (DeepEval is assistive, not sufficient as a sole gate).
4. Cost visibility: tokens and cost-per-paper are first-class metrics.
5. Explainability: store evidence chunk IDs and page references.

## Users
- Teacher/Reviewer: generates, reviews, edits, exports.
- School Admin: manages users, subjects, templates, access.
- Ops/Product: monitors latency, cost, quality, KPIs.

## High-Level Architecture
### System context
- Teacher Portal → Orchestrator API
- Orchestrator → MCP tools + LLM provider
- Data stores → MongoDB Atlas, Redis, Object Storage (S3/Azure Blob)
- Observability → OpenTelemetry + optional LLM tracing (LangSmith/Arize Phoenix)

### Core layers
1. Ingestion Layer: PDF extraction/OCR/layout parsing → Smart Chunks (text + LaTeX + diagram refs + curriculum metadata)
2. Orchestrator Layer: workflow engine for planning, retrieval, generation, evaluation, HITL, export
3. MCP Tool Layer: standardized tools (Syllabus, Retriever, Diagram, Formatter, Evaluation, Analytics)
4. Storage Layer: Atlas Vector Search + Atlas Search + RRF; Redis caches

## Tech Stack (summary)
- Orchestrator: FastAPI (recommended) or Node.js
- Search/DB: MongoDB Atlas (Vector Search + Atlas Search)
- Cache: Redis
- Storage: S3/Azure Blob (PDFs, images, exports)
- Evaluation: DeepEval
- Observability: OpenTelemetry; optional LangSmith/Arize Phoenix

## Build-first Checklist
1. Ingest MVP slice textbooks + Smart Chunk schema
2. Hybrid retrieval + context pack builder
3. Orchestrator generation workflow + evaluation loop
4. Teacher Portal review/edit/export
5. Gold dataset + benchmark harness + KPI dashboard
