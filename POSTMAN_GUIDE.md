# ExamSmith Retrieval API - Postman Collection Guide

## 📥 How to Import

### Method 1: Direct Import (Easiest)
1. **Open Postman** (download from https://www.postman.com/downloads/)
2. Click **File** → **Import** (or use `Ctrl+O`)
3. Select **Upload Files** tab
4. Browse to: `ExamSmith-Retrieval-API.postman_collection.json`
5. Click **Import**

### Method 2: Via Link
1. **Open Postman**
2. Click **Import** button (top-left)
3. Paste the file path or use drag-and-drop

---

## 🔧 Quick Setup

### Step 1: Configure Base URL
1. After importing, look at the **Variables** tab
2. Find `base_url` variable
3. Set to your server URL:
   - **Local**: `http://localhost:8000`
   - **Remote**: `https://your-domain.com`

### Step 2: Start Testing
1. Click any request in the collection
2. Click **Send**
3. View response in the **Response** panel

---

## 📋 Collection Structure

```
ExamSmith Retrieval Backend (Root)
├── Health & Status
│   ├── Health Check               GET /health
│   └── Get Metrics                GET /api/v1/metrics
│
├── Retrieval Endpoints
│   ├── /ask - Student Doubts      POST /api/v1/ask
│   ├── /ask - Semantic Heavy      POST /api/v1/ask (70% Vector)
│   └── /ask - Keyword Heavy       POST /api/v1/ask (30% Vector)
│
├── Question Similarity
│   ├── Find Similar Questions     POST /api/v1/similar-questions
│   ├── Easy Difficulty            POST /api/v1/similar-questions (easy)
│   ├── Medium Difficulty          POST /api/v1/similar-questions (medium)
│   └── Hard Difficulty            POST /api/v1/similar-questions (hard)
│
├── Paper Generation
│   ├── Generate Paper - Basic     POST /api/v1/generate-paper
│   ├── Generate Paper - Difficult POST /api/v1/generate-paper (70% hard)
│   ├── Generate Paper - Easy      POST /api/v1/generate-paper (60% easy)
│   └── Generate Paper - Balanced  POST /api/v1/generate-paper (balanced)
│
└── Answer Evaluation
    ├── Evaluate Answer - With ID  POST /api/v1/evaluate-answer
    ├── Evaluate Answer - Semantic POST /api/v1/evaluate-answer (no ID)
    ├── Evaluate Answer - Short    POST /api/v1/evaluate-answer (MCQ)
    └── Evaluate Answer - Essay    POST /api/v1/evaluate-answer (long)
```

---

## 🧪 Testing Workflow

### 1. Verify Backend is Running
```
Send: Health Check
Expected: status = "healthy", mongodb = "connected"
```

### 2. Test Concept Explanations
```
Send: /ask - Student Doubts
Expected: answer + sources + context_preview
```

### 3. Find Similar Questions
```
Send: Find Similar Questions - No Filter
Expected: list of similar questions with scores
```

### 4. Generate a Paper
```
Send: Generate Paper - Basic
Expected: paper_id + 14 MCQs + essay questions (100 marks)
```

### 5. Evaluate a Student Answer
```
Send: Evaluate Answer - With Question ID
Expected: match_percentage + feedback + improvements
```

### 6. Monitor Performance
```
Send: Get Metrics
Expected: latency stats for each retrieval mode
```

---

## 💡 Example Requests & What They Test

### 1. Health Check
- **Tests**: Server connectivity + MongoDB connection
- **Expected**: 200 OK with status

### 2. /ask - Basic Search
- **Tests**: Hybrid search (50% vector, 50% BM25)
- **Expected**: Explanation from textbook + citations

### 3. /ask - Semantic Heavy (70% vector)
- **Tests**: Vector-dominant search for fuzzy questions
- **Use Case**: Complex, paraphrased questions

### 4. /ask - Keyword Heavy (30% vector)
- **Tests**: BM25-dominant search for exact matches
- **Use Case**: Direct keyword searches

### 5. Similar Questions - Medium Difficulty
- **Tests**: Vector search with difficulty filter
- **Expected**: Questions similar in theme but medium difficulty

### 6. Generate Paper - Difficult (70% hard)
- **Tests**: Paper generation with custom difficulty
- **Expected**: 100-mark paper with mostly hard questions

### 7. Evaluate Answer
- **Tests**: Semantic answer comparison + grading
- **Expected**: Match %, missing points, improvements

### 8. Metrics
- **Tests**: Performance monitoring
- **Expected**: Latency, errors, token usage

---

## 🎯 Pre-configured Test Scenarios

The collection includes **12 pre-built requests** covering:

### Scenario A: Quick Start (5 min)
1. Health Check
2. /ask (basic)
3. Similar Questions (basic)
4. Generate Paper (basic)
5. Evaluate Answer (basic)
6. Metrics

### Scenario B: Hybrid Search Tuning (10 min)
1. /ask - Balanced (50/50)
2. /ask - Semantic Heavy (70/30)
3. /ask - Keyword Heavy (30/70)
→ Compare results to understand weight impact

### Scenario C: Question Difficulty Testing (10 min)
1. Similar Questions (easy)
2. Similar Questions (medium)
3. Similar Questions (hard)
→ Verify difficulty filtering works

### Scenario D: Paper Generation Testing (10 min)
1. Generate Paper - Basic
2. Generate Paper - Easy (60%)
3. Generate Paper - Difficult (70%)
4. Generate Paper - Balanced (25/50/25)
→ Verify difficulty distribution works

### Scenario E: Answer Evaluation Testing (10 min)
1. Evaluate Answer - With Question ID
2. Evaluate Answer - Semantic Search
3. Evaluate Answer - Short Answer
4. Evaluate Answer - Essay
→ Test different answer types

---

## 📊 Response Examples

### ✅ Successful Health Check
```json
{
  "status": "healthy",
  "mongodb": "connected",
  "service": "ExamSmith Retrieval Backend"
}
```

### ✅ Successful /ask Response
```json
{
  "answer": "Personification is a literary device where human qualities are attributed to non-human objects...",
  "sources": [
    {
      "chunk_id": "doc_123",
      "source": "textbook",
      "page": 45,
      "lesson_name": "Lesson 2: Literary Devices"
    }
  ],
  "context_preview": "Personification is a figure of speech...",
  "retrieval_mode": "concept_explanation"
}
```

### ✅ Successful /evaluate-answer Response
```json
{
  "question": "What is personification?",
  "student_answer": "...",
  "official_answer": "...",
  "feedback": {
    "match_percentage": 78,
    "missing_points": ["formal definition"],
    "extra_points": ["good example"],
    "improvements": "Add more formal language...",
    "evidence_chunks": ["Personification is a figure of speech..."]
  },
  "confidence": 0.78
}
```

### ❌ Error Response
```json
{
  "error": "Internal server error",
  "detail": "MongoDB connection failed"
}
```

---

## 🔍 Debugging Tips

### If You Get 500 Error
1. Check if server is running: `uvicorn main:app --reload`
2. Check MongoDB connection in `.env`
3. Check logs in terminal

### If You Get 404 Error
1. Verify `base_url` variable is correct
2. Check if API path is correct (should include `/api/v1`)

### If You Get Empty Results
1. Check MongoDB has data injected
2. Try a simpler query first
3. Check `/metrics` to see if retrieval ran

### If Response is Slow (>1000ms)
1. Check `/metrics` for latency
2. Reduce `top_k` parameter
3. Check MongoDB indexes are created

---

## 🚀 Advanced Usage

### Custom Environment Variables
1. Click environment dropdown (top-right)
2. Create a new environment
3. Add variables:
   - `base_url`: Your server URL
   - `api_key`: If you add authentication later

### Save Responses
1. Right-click response
2. Click **Save Response**
3. Give it a name for comparison

### Create Test Scripts
1. Click **Tests** tab in request
2. Add JavaScript for validation:
```javascript
pm.test("Status is 200", function() {
  pm.response.to.have.status(200);
});

pm.test("Response has answer", function() {
  pm.expect(pm.response.json().answer).to.exist;
});
```

### Run Collection (Test Runner)
1. Click **Run** button (or `Collection → Run`)
2. Select requests to run
3. Click **Run**
4. View results

---

## 📝 Request Template Reference

### /ask Template
```json
{
  "question": "Your question here",
  "hybrid_search": {
    "vector_weight": 0.5,    // 0-1 (how much vector search)
    "bm25_weight": 0.5,      // 0-1 (how much keyword search)
    "top_k": 5               // 1-50 results
  }
}
```

### /similar-questions Template
```json
{
  "question_text": "Question to find similar matches for",
  "top_k": 5,                    // 1-20 results
  "difficulty": null             // "easy", "medium", "hard", or null
}
```

### /generate-paper Template
```json
{
  "year": 2025,
  "difficulty_distribution": {
    "easy": 0.25,
    "medium": 0.5,
    "hard": 0.25
  }
  // OR set to null for default distribution
}
```

### /evaluate-answer Template
```json
{
  "question_text": "The exam question",
  "student_answer": "Student's answer goes here",
  "question_id": "Q15",            // Optional: specific question ID
  "expected_answer": null          // Optional: manual answer key
}
```

---

## ✨ Pro Tips

1. **Duplicate requests** to test variations without editing originals
2. **Use variables** for base_url to switch between environments
3. **Save response bodies** to compare before/after changes
4. **Check metrics** before and after changes to measure impact
5. **Test edge cases**: empty inputs, very long queries, special characters

---

## 🎓 Learning Path

1. Start with **Health Check** (verify connectivity)
2. Try **Basic /ask** (understand retrieval)
3. Experiment with **Hybrid Search weights** (compare results)
4. Test **Different difficulties** (explore filtering)
5. Generate **Papers** (see 100-mark structure)
6. Evaluate **Answers** (understand grading)
7. Check **Metrics** (monitor performance)

---

## 🆘 Support

If you encounter issues:
1. Check `TESTING_GUIDE.md` in the backend folder
2. Review `README.md` for API details
3. Check server logs: `uvicorn main:app --reload --log-level debug`
4. Verify `.env` configuration

---

**Happy Testing! 🚀**

File Location: `ExamSmith-Retrieval-API.postman_collection.json`
