# 🚀 ExamSmith Retrieval API - Postman Quick Start

## 📥 Import in 30 Seconds

### Step 1: Get Postman
```
Download: https://www.postman.com/downloads/
```

### Step 2: Import Collection
```
File → Import → ExamSmith-Retrieval-API.postman_collection.json
```

### Step 3: Set Base URL
```
Click: {{base_url}} variable (top-right dropdown)
Edit: http://localhost:8000 (or your server URL)
```

### Step 4: Test!
```
Click any request → Send
```

---

## ✅ Verify Setup (5 minutes)

### Test 1: Health Check
```
Request: GET /health
Expected: {"status": "healthy", "mongodb": "connected"}
Status: 200 OK ✅
```

### Test 2: Ask Endpoint
```
Request: POST /ask
Body: {"question": "What is personification?", ...}
Expected: LLM-generated explanation + sources
Status: 200 OK ✅
```

### Test 3: Similar Questions
```
Request: POST /similar-questions
Body: {"question_text": "...", "top_k": 5}
Expected: List of similar exam questions
Status: 200 OK ✅
```

### Test 4: Generate Paper
```
Request: POST /generate-paper
Body: {"year": 2025}
Expected: 100-mark TN SSLC paper with questions
Status: 200 OK ✅
```

### Test 5: Evaluate Answer
```
Request: POST /evaluate-answer
Body: {"question_text": "...", "student_answer": "..."}
Expected: Match % + feedback
Status: 200 OK ✅
```

---

## 📚 Request Examples by Endpoint

### 1️⃣ Ask (Student Doubts)

**Balanced Search (50% Vector, 50% BM25)**
```bash
POST http://localhost:8000/api/v1/ask

{
  "question": "What is the theme of the first lesson?",
  "hybrid_search": {
    "vector_weight": 0.5,
    "bm25_weight": 0.5,
    "top_k": 5
  }
}
```

**Semantic Search (70% Vector)**
```bash
{
  "question": "Explain the character's emotional journey",
  "hybrid_search": {
    "vector_weight": 0.7,
    "bm25_weight": 0.3,
    "top_k": 5
  }
}
```

**Keyword Search (70% BM25)**
```bash
{
  "question": "define personification lesson 2",
  "hybrid_search": {
    "vector_weight": 0.3,
    "bm25_weight": 0.7,
    "top_k": 5
  }
}
```

---

### 2️⃣ Similar Questions

**Find Any Similar Questions**
```bash
POST http://localhost:8000/api/v1/similar-questions

{
  "question_text": "What is the main theme?",
  "top_k": 5,
  "difficulty": null
}
```

**Easy Questions Only**
```bash
{
  "question_text": "Define metaphor",
  "top_k": 5,
  "difficulty": "easy"
}
```

**Hard Questions Only**
```bash
{
  "question_text": "Critically analyze the author's use of symbolism",
  "top_k": 5,
  "difficulty": "hard"
}
```

---

### 3️⃣ Generate Paper

**Standard Paper**
```bash
POST http://localhost:8000/api/v1/generate-paper

{
  "year": 2025,
  "difficulty_distribution": null
}
```

**Easy Paper (60% easy)**
```bash
{
  "year": 2025,
  "difficulty_distribution": {
    "easy": 0.6,
    "medium": 0.3,
    "hard": 0.1
  }
}
```

**Hard Paper (70% hard)**
```bash
{
  "year": 2025,
  "difficulty_distribution": {
    "easy": 0.1,
    "medium": 0.2,
    "hard": 0.7
  }
}
```

---

### 4️⃣ Evaluate Answer

**With Question ID**
```bash
POST http://localhost:8000/api/v1/evaluate-answer

{
  "question_text": "What is personification?",
  "student_answer": "When you give human qualities to objects",
  "question_id": "Q5",
  "expected_answer": null
}
```

**Without Question ID (Semantic Search)**
```bash
{
  "question_text": "Explain the theme of the story",
  "student_answer": "The story teaches about resilience and hope",
  "question_id": null,
  "expected_answer": null
}
```

---

## 🎯 Common Test Scenarios

### Scenario 1: Quick Verification (5 min)
1. ✅ Health Check → should return healthy
2. ✅ /ask → should return explanation
3. ✅ /metrics → should show stats

**Expected**: All 200 OK

---

### Scenario 2: Hybrid Search Comparison (10 min)
1. Send `/ask` with 50/50 weights
2. Send same question with 70/30 weights
3. Send same question with 30/70 weights
4. Compare results

**Expected**: Different results showing weight impact

---

### Scenario 3: Answer Evaluation (5 min)
1. Send `/evaluate-answer` with good answer
2. Send `/evaluate-answer` with poor answer
3. Compare match_percentage

**Expected**: Good answer > 75%, Poor answer < 50%

---

### Scenario 4: Full Paper Test (5 min)
1. Generate basic paper
2. Generate easy paper
3. Generate hard paper
4. Compare question distributions

**Expected**: 100 marks in each, different difficulties

---

## 📊 Response Codes

| Code | Meaning | Fix |
|------|---------|-----|
| 200 | ✅ Success | All good! |
| 400 | ❌ Bad request | Check JSON syntax |
| 404 | ❌ Not found | Check URL path |
| 422 | ❌ Validation error | Check required fields |
| 500 | ❌ Server error | Check MongoDB/Groq connection |

---

## 🔧 Troubleshooting

### "Connection refused"
```
✗ Server not running
✓ Start: uvicorn main:app --reload
```

### "MongoDB connection failed"
```
✗ MongoDB not connected
✓ Check MONGODB_URI in .env
✓ Check IP whitelist in MongoDB Atlas
```

### "Groq API error"
```
✗ Invalid API key
✓ Check GROQ_API_KEY in .env
```

### "Empty results"
```
✗ No data in MongoDB
✓ Check data injection step
✓ Verify collections exist
```

---

## 💡 Pro Tips

### Tip 1: Save Responses
Right-click response → Save Response → Name it
*(Compare before/after changes)*

### Tip 2: Duplicate Requests
Right-click request → Duplicate
*(Test variations safely)*

### Tip 3: Use Pre-request Scripts
1. Click **Pre-request Script** tab
2. Auto-generate question ID:
```javascript
pm.globals.set("timestamp", new Date().getTime());
```

### Tip 4: Use Test Scripts
1. Click **Tests** tab
2. Validate responses:
```javascript
pm.test("Response status is 200", function() {
    pm.response.to.have.status(200);
});

pm.test("Response has answer", function() {
    pm.expect(pm.response.json()).to.have.property('answer');
});
```

### Tip 5: Monitor Performance
1. Check `/metrics` endpoint
2. Note avg latency for each mode
3. Optimize if needed

---

## 📋 Collection Contents

### Health Checks (2)
- [ ] Health Check
- [ ] Get Metrics

### Retrieval (3)
- [ ] /ask - Balanced
- [ ] /ask - Semantic Heavy (70%)
- [ ] /ask - Keyword Heavy (30%)

### Question Similarity (4)
- [ ] Similar Questions - Any
- [ ] Similar Questions - Easy
- [ ] Similar Questions - Medium
- [ ] Similar Questions - Hard

### Paper Generation (4)
- [ ] Generate Paper - Basic
- [ ] Generate Paper - Easy (60%)
- [ ] Generate Paper - Difficult (70%)
- [ ] Generate Paper - Balanced

### Answer Evaluation (4)
- [ ] Evaluate Answer - With ID
- [ ] Evaluate Answer - Semantic
- [ ] Evaluate Answer - Short
- [ ] Evaluate Answer - Essay

**Total: 17 Pre-built Requests** ✅

---

## 🎓 Learning Path

```
Day 1:
  → Import collection
  → Set base_url variable
  → Run Health Check
  
Day 2:
  → Try /ask with different weights
  → Compare results
  
Day 3:
  → Generate papers (easy/hard)
  → Evaluate answers
  
Day 4:
  → Use /metrics to monitor
  → Optimize if needed
```

---

## 📞 Need Help?

1. **API Documentation**: See `README.md`
2. **Testing Guide**: See `TESTING_GUIDE.md`
3. **Server Logs**: Check terminal running `uvicorn`
4. **Collection File**: `ExamSmith-Retrieval-API.postman_collection.json`

---

## 🚀 You're Ready!

```
✅ Postman installed
✅ Collection imported
✅ Base URL configured
✅ Ready to test!

Click a request → Click Send → View Response

Happy Testing! 🎉
```

---

**Location**: `ExamSmith-Retrieval-API.postman_collection.json`

**Size**: ~50KB with 17 requests + examples + documentation

**Last Updated**: 2026-01-20
