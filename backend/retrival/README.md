# ExamSmith Retrieval Backend

AI-powered retrieval and answer evaluation system for Tamil Nadu SSLC (10th Standard) English.

## 📋 Project Structure

```
backend/retrival/
├── config.py                 # Settings from .env
├── observability.py          # Logging & performance metrics
├── models.py                 # Pydantic request/response schemas
├── main.py                   # FastAPI app entry point
├── api.py                    # API route handlers
├── llm/
│   ├── base.py              # Abstract LLM provider
│   ├── groq_provider.py      # Groq implementation
│   └── factory.py           # LLM provider factory
├── mongo/
│   ├── client.py            # MongoDB connection manager
│   └── search.py            # Hybrid search (BM25 + Vector) with RRF
├── retriever/
│   ├── base.py              # Abstract retriever strategy
│   ├── concept_explanation.py   # Textbook hybrid search
│   ├── question_similarity.py   # Question vector search
│   ├── paper_generation.py      # Question collection retrieval
│   └── answer_evaluation.py     # Official answer + evidence retrieval
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your credentials:
# - MONGODB_URI: Your MongoDB Atlas connection string
# - GROQ_API_KEY: Your Groq API key
# - GROQ_MODEL: Set to "meta-llama/llama-4-maverick-17b-128e-instruct"
```

### 3. Run Server

```bash
# Development mode (auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python main.py
```

Server will be available at: `http://localhost:8000`

## 📚 API Endpoints

### 1. `/api/v1/ask` (POST)

**Purpose**: Student doubts and concept explanations

**Request**:
```json
{
  "question": "What is the theme of the story?",
  "hybrid_search": {
    "vector_weight": 0.5,
    "bm25_weight": 0.5,
    "top_k": 5
  }
}
```

**Response**:
```json
{
  "answer": "The story explores themes of...",
  "sources": [
    {
      "chunk_id": "doc_123",
      "source": "textbook",
      "lesson_name": "Lesson 1: The Story"
    }
  ],
  "context_preview": "The story is about...",
  "retrieval_mode": "concept_explanation"
}
```

---

### 2. `/api/v1/similar-questions` (POST)

**Purpose**: Find similar exam questions

**Request**:
```json
{
  "question_text": "What is the main character's motivation?",
  "top_k": 5,
  "difficulty": "medium"
}
```

**Response**:
```json
{
  "questions": [
    {
      "question_number": "15",
      "question_text": "Describe the main character's motivations.",
      "question_type": "short_answer",
      "answer_key": "The character was motivated by...",
      "marks": 2,
      "year": 2024,
      "similarity_score": 0.92
    }
  ],
  "total_found": 1
}
```

---

### 3. `/api/v1/generate-paper` (POST)

**Purpose**: Generate TN SSLC model question papers

**Request**:
```json
{
  "year": 2025,
  "difficulty_distribution": {
    "easy": 0.2,
    "medium": 0.5,
    "hard": 0.3
  }
}
```

**Response**:
```json
{
  "paper_id": "uuid-1234",
  "status": "generated",
  "questions": [
    {
      "question_number": "1",
      "question_text": "Choose the correct synonym...",
      "type": "mcq",
      "marks": 1,
      "section": "part_i"
    }
  ],
  "total_marks": 100,
  "estimated_time_minutes": 180
}
```

---

### 4. `/api/v1/evaluate-answer` (POST)

**Purpose**: Evaluate student answers

**Request**:
```json
{
  "question_text": "Explain the theme of the story",
  "student_answer": "The story explores themes of resilience and hope...",
  "question_id": "Q15",
  "expected_answer": null
}
```

**Response**:
```json
{
  "question": "Explain the theme of the story",
  "student_answer": "The story explores themes of resilience and hope...",
  "official_answer": "The theme is about overcoming adversity...",
  "feedback": {
    "match_percentage": 75,
    "missing_points": ["mention of sacrifice"],
    "extra_points": ["good contextual reference"],
    "improvements": "Add more specific examples from the text...",
    "evidence_chunks": ["relevant textbook excerpts..."]
  },
  "confidence": 0.75
}
```

---

### 5. `/health` (GET)

**Purpose**: Health check

**Response**:
```json
{
  "status": "healthy",
  "mongodb": "connected",
  "service": "ExamSmith Retrieval Backend"
}
```

---

### 6. `/api/v1/metrics` (GET)

**Purpose**: Retrieval performance metrics

**Response**:
```json
{
  "retrieval_stats": {
    "concept_explanation": {
      "avg_latency_ms": 245.3,
      "max_latency_ms": 532.1,
      "total_searches": 42,
      "error_rate": 2.4
    }
  },
  "timestamp": "2026-01-20T10:30:45.123456"
}
```

## 🔧 Configuration

### Hybrid Search Tuning

Control BM25 vs Vector search weights via API payload:

```json
{
  "hybrid_search": {
    "vector_weight": 0.6,      // 60% vector
    "bm25_weight": 0.4,        // 40% BM25
    "top_k": 5
  }
}
```

**Recommendation**:
- **0.5 / 0.5**: Balanced (default)
- **0.7 / 0.3**: Semantic-heavy (better for fuzzy questions)
- **0.3 / 0.7**: Keyword-heavy (better for exact matches)

### MongoDB Indexes (Required)

Before using, ensure indexes are created in MongoDB Atlas:

**Textbook Collection (`10_books.english`)**:
```
- Atlas Search Index: "BM25" on "content" field
- Vector Index: "vector" on "embedding" field (1024-dim)
```

**Question Papers Collection (`10_questionpapers.2025_public`)**:
```
- Vector Index: "vector" on "embedding" field (1024-dim)
```

## 🎯 Retrieval Modes

### 1. Concept Explanation (Hybrid)
- **Uses**: Textbook collection
- **Search**: BM25 + Vector (configurable weights)
- **Output**: Explanation + citations

### 2. Question Similarity (Vector)
- **Uses**: Question papers
- **Search**: Vector search only
- **Output**: Similar questions + answer keys

### 3. Paper Generation (Filtered)
- **Uses**: Question papers (all sections)
- **Search**: Metadata-based filtering
- **Output**: Structured paper with 100 marks

### 4. Answer Evaluation (Hybrid + Comparison)
- **Uses**: Question papers + Textbook
- **Search**: Hybrid for evidence, direct lookup for official answer
- **Output**: Match % + feedback + improvements

## 📊 Error Handling

All endpoints gracefully handle MongoDB unavailability:

```json
{
  "error": "Internal server error",
  "detail": "MongoDB connection failed"
}
```

HTTP Status Codes:
- `200`: Success
- `404`: Question/content not found
- `422`: Validation error (invalid input)
- `500`: Server error

## 🔐 Environment Variables

| Variable | Required | Default | Example |
|----------|----------|---------|---------|
| MONGODB_URI | ✅ | - | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| GROQ_API_KEY | ✅ | - | `gsk_...` |
| GROQ_MODEL | ❌ | `meta-llama/llama-4-maverick-17b-128e-instruct` | `mixtral-8x7b-32768` |
| FASTAPI_PORT | ❌ | `8000` | `8000` |
| HYBRID_SEARCH_RRF_K | ❌ | `60` | `60` |
| HYBRID_SEARCH_DEFAULT_VECTOR_WEIGHT | ❌ | `0.5` | `0.6` |
| HYBRID_SEARCH_DEFAULT_BM25_WEIGHT | ❌ | `0.5` | `0.4` |
| LOG_LEVEL | ❌ | `INFO` | `DEBUG` |

## 📈 Performance Monitoring

View real-time metrics via `/api/v1/metrics`:

```python
import requests

metrics = requests.get("http://localhost:8000/api/v1/metrics").json()
print(metrics["retrieval_stats"]["concept_explanation"])
# Output:
# {
#   "avg_latency_ms": 245.3,
#   "max_latency_ms": 532.1,
#   "total_searches": 42,
#   "error_rate": 2.4
# }
```

## 🚨 Troubleshooting

### MongoDB Connection Failed
```
✗ MongoDB connection failed: [Errno 11001] getaddrinfo failed
```
**Solution**: Check `MONGODB_URI` in `.env` and ensure IP whitelist is configured in MongoDB Atlas.

### Groq API Error
```
groq.error.APIError: 401 Unauthorized
```
**Solution**: Verify `GROQ_API_KEY` in `.env` is correct.

### Vector Search Not Working
```
$search operator is not allowed for this project
```
**Solution**: Ensure MongoDB Atlas Vector Search index is created on `embedding` field.

## 🔮 Future Enhancements

- [ ] OpenAI / Gemini provider support
- [ ] Advanced feedback loop learning
- [ ] Teacher HITL approval workflow
- [ ] Multi-language support
- [ ] Rate limiting per user
- [ ] OpenTelemetry tracing
- [ ] Query caching layer

## 📝 License

ExamSmith © 2026

## 👤 Contact

For issues or suggestions, contact the development team.
