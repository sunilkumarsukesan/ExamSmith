# ExamSmith Retrieval Backend - Testing Guide

## 📌 Quick Test Checklist

Before running tests, ensure:
- [ ] `.env` is configured with valid credentials
- [ ] MongoDB Atlas connection is active
- [ ] Groq API key is valid
- [ ] MongoDB indexes are created (BM25 + Vector)

---

## 🏃 Running Tests

### Start Server
```bash
# Terminal 1: Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Output should show:
# INFO:     Application startup complete
# INFO:     ✓ MongoDB connected
```

### Health Check
```bash
# Terminal 2: Test health endpoint
curl http://localhost:8000/health

# Expected:
# {"status": "healthy", "mongodb": "connected", "service": "ExamSmith Retrieval Backend"}
```

---

## 🧪 API Testing with cURL

### 1. `/ask` - Student Doubts

**Test Case 1: Basic Question**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the theme of the first lesson?",
    "hybrid_search": {
      "vector_weight": 0.5,
      "bm25_weight": 0.5,
      "top_k": 3
    }
  }' | jq .
```

**Test Case 2: Semantic-heavy Search**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain the main characters motivations",
    "hybrid_search": {
      "vector_weight": 0.7,
      "bm25_weight": 0.3,
      "top_k": 5
    }
  }' | jq .
```

---

### 2. `/similar-questions` - Find Similar Exam Questions

**Test Case 1: Basic Similarity Search**
```bash
curl -X POST http://localhost:8000/api/v1/similar-questions \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is the main character afraid of?",
    "top_k": 3,
    "difficulty": null
  }' | jq .
```

**Test Case 2: Medium Difficulty Only**
```bash
curl -X POST http://localhost:8000/api/v1/similar-questions \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Describe the themes present in the story",
    "top_k": 5,
    "difficulty": "medium"
  }' | jq .
```

---

### 3. `/generate-paper` - Generate Question Paper

**Test Case 1: Basic Paper Generation**
```bash
curl -X POST http://localhost:8000/api/v1/generate-paper \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2025,
    "difficulty_distribution": null
  }' | jq .
```

**Test Case 2: With Difficulty Distribution**
```bash
curl -X POST http://localhost:8000/api/v1/generate-paper \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2025,
    "difficulty_distribution": {
      "easy": 0.2,
      "medium": 0.5,
      "hard": 0.3
    }
  }' | jq .
```

**Expected Response Structure**:
```json
{
  "paper_id": "uuid-string",
  "status": "generated",
  "questions": [
    {
      "question_number": "1",
      "question_text": "...",
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

### 4. `/evaluate-answer` - Check Student Answer

**Test Case 1: Evaluate with Question ID**
```bash
curl -X POST http://localhost:8000/api/v1/evaluate-answer \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Explain the theme of the story",
    "student_answer": "The story explores themes of resilience and overcoming adversity through the main character journey.",
    "question_id": "Q15",
    "expected_answer": null
  }' | jq .
```

**Test Case 2: Evaluate with Semantic Search**
```bash
curl -X POST http://localhost:8000/api/v1/evaluate-answer \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is the significance of the ending?",
    "student_answer": "The ending shows hope and redemption for the character.",
    "question_id": null,
    "expected_answer": null
  }' | jq .
```

**Expected Response**:
```json
{
  "question": "Explain the theme of the story",
  "student_answer": "...",
  "official_answer": "...",
  "feedback": {
    "match_percentage": 78,
    "missing_points": ["mention of sacrifice"],
    "extra_points": ["good contextual reference"],
    "improvements": "Add more specific examples...",
    "evidence_chunks": ["chunk 1", "chunk 2"]
  },
  "confidence": 0.78
}
```

---

### 5. `/metrics` - Performance Monitoring

```bash
curl http://localhost:8000/api/v1/metrics | jq .

# Expected:
# {
#   "retrieval_stats": {
#     "concept_explanation": {
#       "avg_latency_ms": 245.3,
#       "max_latency_ms": 532.1,
#       "total_searches": 42,
#       "error_rate": 2.4
#     },
#     ...
#   },
#   "timestamp": "2026-01-20T10:30:45.123456"
# }
```

---

## 🐍 Python Testing Script

Save as `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_ask():
    """Test /ask endpoint"""
    print("🧪 Testing /ask endpoint...")
    response = requests.post(
        f"{BASE_URL}/ask",
        json={
            "question": "What is a metaphor?",
            "hybrid_search": {
                "vector_weight": 0.5,
                "bm25_weight": 0.5,
                "top_k": 3
            }
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_similar_questions():
    """Test /similar-questions endpoint"""
    print("🧪 Testing /similar-questions endpoint...")
    response = requests.post(
        f"{BASE_URL}/similar-questions",
        json={
            "question_text": "What is the theme of the story?",
            "top_k": 3,
            "difficulty": None
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_generate_paper():
    """Test /generate-paper endpoint"""
    print("🧪 Testing /generate-paper endpoint...")
    response = requests.post(
        f"{BASE_URL}/generate-paper",
        json={
            "year": 2025,
            "difficulty_distribution": None
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_evaluate_answer():
    """Test /evaluate-answer endpoint"""
    print("🧪 Testing /evaluate-answer endpoint...")
    response = requests.post(
        f"{BASE_URL}/evaluate-answer",
        json={
            "question_text": "Explain the theme",
            "student_answer": "The theme is about resilience.",
            "question_id": None,
            "expected_answer": None
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_metrics():
    """Test /metrics endpoint"""
    print("🧪 Testing /metrics endpoint...")
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if __name__ == "__main__":
    print("=" * 60)
    print("ExamSmith Retrieval Backend - API Tests")
    print("=" * 60 + "\n")
    
    try:
        test_ask()
        test_similar_questions()
        test_generate_paper()
        test_evaluate_answer()
        test_metrics()
        
        print("✅ All tests completed!")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
```

**Run tests**:
```bash
python test_api.py
```

---

## 🔍 Debugging

### Enable Debug Logging
```python
# In main.py, change:
logging.basicConfig(level=logging.DEBUG)  # Instead of INFO
```

### Check MongoDB Connection
```bash
# Test MongoDB directly
python -c "
from pymongo import MongoClient
from config import settings

client = MongoClient(settings.mongodb_uri)
print('Collections:', client[settings.mongodb_db_textbook].list_collection_names())
client.close()
"
```

### Verify Groq API
```bash
# Test Groq API key
python -c "
from groq import Groq
from config import settings

client = Groq(api_key=settings.groq_api_key)
response = client.chat.completions.create(
    model=settings.groq_model,
    messages=[{'role': 'user', 'content': 'Test'}],
    max_tokens=10
)
print('✓ Groq API working')
"
```

---

## 📊 Performance Benchmarks (Target)

| Endpoint | Latency (ms) | Notes |
|----------|--------------|-------|
| `/ask` (hybrid) | 200-500 | BM25 + Vector |
| `/similar-questions` | 150-300 | Vector only |
| `/generate-paper` | 100-200 | Metadata filter |
| `/evaluate-answer` | 300-600 | Hybrid + LLM |

---

## 🚨 Common Issues & Fixes

### Issue: "MongoDB connection failed"
```
Solution: Check MONGODB_URI in .env
- Verify Atlas IP whitelist includes your IP
- Test connection: mongosh <MONGODB_URI>
```

### Issue: "Groq API 401 Unauthorized"
```
Solution: Verify GROQ_API_KEY in .env
- Get key from: https://console.groq.com/keys
- Ensure key hasn't expired
```

### Issue: "No results found"
```
Solution: Check MongoDB indexes
- Ensure BM25 index on textbook.content
- Ensure Vector index on embedding fields
- Verify data was injected
```

### Issue: "JSON decode error"
```
Solution: Groq response parsing failed
- Check LLM model output format
- Increase max_tokens if response is cut off
- Retry with lower temperature
```

---

## 📝 Test Report Template

```
Test Date: 2026-01-20
Tester: [Name]

[✅ PASS] /ask endpoint
[✅ PASS] /similar-questions endpoint
[⚠️ WARN] /generate-paper - slow (~800ms)
[❌ FAIL] /evaluate-answer - MongoDB connection error

Issues Found:
1. Slow paper generation - need index optimization
2. Missing question metadata

Recommendations:
1. Add composite index on (section, difficulty)
2. Implement paper caching
```

---

## 🎯 Test Coverage Goals

- [ ] All 4 endpoints functional
- [ ] Hybrid search working with configurable weights
- [ ] Error handling for missing MongoDB
- [ ] Error handling for Groq API failures
- [ ] Response validation matches schema
- [ ] Metrics endpoint tracking calls
- [ ] Citations populated correctly
- [ ] Performance within 600ms SLA

---

Good luck testing! 🚀
