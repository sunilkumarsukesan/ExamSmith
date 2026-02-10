# ExamSmith – Technical Documentation

## 1. Project Overview

ExamSmith is an AI-powered exam question generation system built using a Retrieval-Augmented Generation (RAG) architecture. The system ingests academic content such as textbooks and past question papers, converts them into embeddings, retrieves relevant context on demand, and generates exam-aligned questions using Large Language Models (LLMs).

The project is designed as a modular, scalable, and production-ready backend with a separate frontend interface.

---

## 2. High-Level Architecture

The system is divided into four major layers:

- Frontend (User Interface)
- Backend APIs (FastAPI)
- Retrieval and Generation Layer (RAG)
- Storage Layer (Metadata DB + Vector DB)

---

## 3. Repository Structure

ExamSmith/
│
├── Frontend/
│ ├── public/
│ ├── src/
│ ├── package.json
│ └── README.md
│
├── backend/
│ ├── injection/
│ │ ├── api/
│ │ ├── services/
│ │ ├── pipelines/
│ │ ├── models/
│ │ ├── utils/
│ │ └── main.py
│ │
│ ├── retrival/
│ │ ├── api/
│ │ ├── llm/
│ │ ├── retrievers/
│ │ ├── generators/
│ │ ├── auth/
│ │ ├── schemas/
│ │ └── main.py
│ │
│ ├── common/
│ ├── config/
│ └── requirements.txt
│
├── data/
│ ├── raw/
│ ├── processed/
│ └── evaluation/
│
├── deepeval-modified/
│
├── docs/
│
├── SETUP_DEV.bat
├── SETUP_DEV.sh
└── README.md


---

## 4. Backend Overview

The backend is implemented using FastAPI and is split into two independent services:

- Injection Service – Handles data ingestion and embedding
- Retrieval Service – Handles query processing and question generation

Each service can be deployed independently.

---

## 5. Injection Service (backend/injection)

### Purpose
The Injection Service is responsible for converting raw academic content into structured, searchable knowledge.

### Responsibilities
- Accept content uploads (files or structured JSON)
- Clean and normalize text
- Chunk large documents
- Generate embeddings
- Store metadata and embeddings in databases

### Key Components
- `api/` – REST API routes
- `pipelines/` – End-to-end ingestion workflows
- `services/` – Business logic
- `models/` – Data models
- `utils/` – Helper functions

### Key APIs
- `POST /ingest/file`
- `POST /ingest/json`
- `GET /ingest/status/{job_id}`
- `GET /health`

---

## 6. Retrieval Service (backend/retrival)

### Purpose
The Retrieval Service retrieves relevant context from stored data and generates exam questions using LLMs.

### Responsibilities
- Authenticate requests using JWT
- Perform vector or hybrid retrieval
- Select relevant context
- Generate structured questions

### Key Components
- `api/` – Query and generation endpoints
- `retrievers/` – Vector and hybrid retrieval logic
- `generators/` – Question generation logic
- `llm/` – LLM abstraction layer
- `auth/` – Authentication and authorization
- `schemas/` – Request and response schemas

### Key APIs
- `POST /query`
- `POST /generate/questions`
- `POST /auth/login`
- `GET /health`

---

## 7. Retrieval Strategy

Different content types use different retrieval strategies:

- Textbooks:
  - Hybrid search (BM25 + Vector)
- Question Papers:
  - Vector-only search

Retrieval is performed at chunk level with metadata-based filtering.

---

## 8. LLM Abstraction Layer

The LLM layer is designed to be provider-agnostic.

### Features
- Factory-based LLM selection
- Easy switching between LLM providers
- Centralized prompt handling
- Configurable temperature and token limits

---

## 9. Storage Layer

### Metadata Storage
- MongoDB
- Stores documents, chunks, metadata, and ingestion status

### Vector Storage
- Vector Database (pluggable)
- Stores embeddings for semantic search

---

## 10. Authentication & Security

- JWT-based authentication
- Password hashing utilities
- Dependency-injected security in FastAPI
- Role-ready architecture for future RBAC

---

## 11. Frontend Overview

The frontend provides a web-based interface to interact with the backend APIs.

### Responsibilities
- Upload content
- Submit queries
- Display generated questions
- Communicate via REST APIs

The frontend is decoupled and replaceable.

---

## 12. Evaluation & Quality Checks

- Evaluation pipeline using a modified DeepEval framework
- Metrics stored in JSON format
- Supports qualitative and quantitative assessment of generated outputs

---

## 13. End-to-End Flow

1. User uploads academic content
2. Injection service processes and embeds content
3. Data is stored in databases
4. User submits a query
5. Retrieval service fetches relevant context
6. LLM generates exam-aligned questions
7. Results are returned to the frontend

---

## 14. Tech Stack

Backend:
- Python
- FastAPI

AI / NLP:
- Large Language Models
- Embedding Models
- Retrieval-Augmented Generation (RAG)

Databases:
- MongoDB
- Vector Database

Frontend:
- JavaScript
- Node.js

---

## 15. Future Improvements

- Role-based access control
- Difficulty-level tuning
- PDF export of generated questions
- Multi-subject and multi-language support
- Advanced evaluation dashboards

---

## 16. Conclusion

ExamSmith is a modular, scalable, and production-ready AI system focused on automating exam question generation using modern RAG-based architectures.
