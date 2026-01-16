
FINAL INSTRUCTION FILE
FastAPI-based JSON → MongoDB Injection Pipeline (with Mistral Embeddings)

OBJECTIVE
Build a FastAPI-based ingestion service that:
- Accepts chunked textbook JSON
- Deduplicates content
- Generates embeddings using Mistral embedding model
- Injects data into MongoDB Atlas
- Runs repeatedly without duplicates
- Exposes progress-aware ingestion APIs
- Stores secrets in .env
- Is UI-consumable

PROJECT STRUCTURE
project-root/
├── data/
│   └── failed_records.json
├── src/
│   ├── main.py
│   ├── api.py
│   ├── ingest_service.py
│   ├── job_manager.py
│   ├── embedder.py
│   ├── mongo_client.py
│   ├── deduplicator.py
│   ├── models.py
│   └── config.py
├── .env
├── requirements.txt
└── INSTRUCTIONS.md

ENVIRONMENT VARIABLES (.env)
MONGODB_URI=
MONGODB_DB_NAME=
MONGODB_COLLECTION_NAME=

MISTRAL_API_KEY=
MISTRAL_EMBEDDING_MODEL=mistral-embed
MISTRAL_EMBEDDING_DIM=1024

API_HOST=0.0.0.0
API_PORT=8000

BATCH_SIZE=32
FAILED_RECORDS_PATH=data/failed_records.json

INPUT JSON SCHEMA
{
  "content": "string",
  "embedding": [],
  "is_table": false,
  "table_json": null,
  "table_markdown": null,
  "metadata": {}
}

API ENDPOINTS
GET /health
POST /ingest/json
GET /ingest/status/{job_id}

DEDUPLICATION
- Compute sha256(content)
- Store as content_hash
- MongoDB upsert using content_hash

EMBEDDING RULES
- Embed only content
- Batch embedding
- Async HTTP calls
- Retry failures
- Validate vector dimension

MONGODB DOCUMENT
{
  "content": "...",
  "content_hash": "...",
  "embedding": [...],
  "is_table": false,
  "table_json": null,
  "table_markdown": null,
  "metadata": {},
  "created_at": ISODate(),
  "updated_at": ISODate()
}

INGESTION FLOW
1. Create job
2. Run ingestion in background
3. Read JSON
4. Deduplicate
5. Batch embed
6. Upsert MongoDB
7. Update progress
8. Log failures
9. Complete job

FAILURE HANDLING
- Append failures to data/failed_records.json
- Do not crash pipeline

REQUIREMENTS
fastapi
uvicorn
pymongo
python-dotenv
requests
tenacity
tqdm
pydantic
python-multipart

RUN COMMAND
uvicorn src.main:app --host 0.0.0.0 --port 8000
