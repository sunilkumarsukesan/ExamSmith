# 📮 Postman Collection - Complete Package

## ✅ What You Got

### Main Files Created
1. **`ExamSmith-Retrieval-API.postman_collection.json`** (50KB)
   - 17 pre-built requests
   - All 4 API endpoints
   - Request examples with variations
   - Response examples
   - Variable configuration

2. **`POSTMAN_GUIDE.md`**
   - Detailed import instructions
   - Testing workflows
   - Response examples
   - Debugging tips
   - Advanced usage

3. **`POSTMAN_QUICK_START.md`**
   - 30-second quick start
   - Common test scenarios
   - Request templates
   - Troubleshooting

---

## 📥 One-Minute Setup

### Step 1: Download Postman
```
https://www.postman.com/downloads/
```

### Step 2: Import Collection
```
Postman → File → Import → Select JSON file
```

### Step 3: Configure URL
```
Set {{base_url}} = http://localhost:8000
```

### Step 4: Send Request
```
Click any request → Send
```

---

## 📊 Collection Overview

```
17 Pre-built Requests:

Health & Status (2 requests)
├── Health Check                          → Verify server
└── Get Metrics                           → Performance stats

Retrieval Endpoints (3 requests)
├── /ask - Balanced                       → 50/50 search
├── /ask - Semantic Heavy                 → 70% vector
└── /ask - Keyword Heavy                  → 70% BM25

Question Similarity (4 requests)
├── Find Similar Questions                → All difficulties
├── Find Similar Questions - Easy         → Easy only
├── Find Similar Questions - Medium       → Medium only
└── Find Similar Questions - Hard         → Hard only

Paper Generation (4 requests)
├── Generate Paper - Basic                → Default
├── Generate Paper - Easy                 → 60% easy
├── Generate Paper - Difficult            → 70% hard
└── Generate Paper - Balanced             → 25/50/25

Answer Evaluation (4 requests)
├── Evaluate Answer - With Question ID    → ID lookup
├── Evaluate Answer - Semantic Search     → No ID
├── Evaluate Answer - Short Answer        → MCQ type
└── Evaluate Answer - Essay               → Long form
```

---

## 🎯 Use Cases

### Use Case 1: Hybrid Search Tuning
1. Send `/ask` with 50/50 weights
2. Send `/ask` with 70/30 weights
3. Send `/ask` with 30/70 weights
4. Compare results to understand impact

### Use Case 2: Answer Evaluation Testing
1. Send good student answer
2. Send poor student answer
3. Compare match_percentage
4. Verify feedback is helpful

### Use Case 3: Paper Generation Validation
1. Generate easy paper (60% easy)
2. Generate hard paper (70% hard)
3. Verify mark distribution
4. Check question variety

### Use Case 4: Performance Monitoring
1. Send multiple requests
2. Check `/metrics` endpoint
3. Monitor latency trends
4. Identify bottlenecks

---

## 🔍 Request Details

### All Requests Include
✅ Pre-filled headers (Content-Type)
✅ Pre-filled body with realistic data
✅ Description of what it tests
✅ Expected response example
✅ Success criteria

### Easy to Modify
- Change question text
- Change weights (0.3-0.7)
- Change difficulty levels
- Change top_k values
- Test edge cases

---

## 📈 Testing Progression

### Level 1: Verification (5 min)
- [ ] Health Check
- [ ] /ask (basic)
- [ ] /metrics

### Level 2: Feature Testing (15 min)
- [ ] All 4 endpoints
- [ ] All difficulty levels
- [ ] Different weights

### Level 3: Advanced Testing (30 min)
- [ ] Edge cases
- [ ] Performance tuning
- [ ] Error scenarios

### Level 4: Load Testing
- [ ] Run collection multiple times
- [ ] Monitor latency growth
- [ ] Check error handling

---

## 💾 File Sizes & Format

| File | Size | Format |
|------|------|--------|
| ExamSmith-Retrieval-API.postman_collection.json | ~50KB | JSON |
| POSTMAN_GUIDE.md | ~15KB | Markdown |
| POSTMAN_QUICK_START.md | ~8KB | Markdown |

**Total**: ~73KB - Easy to share via email or Git

---

## 🎓 Learning Features

### Built-In Examples
- Every request has example data
- Every response has example output
- Comments explain what each field does

### Variations Included
- 3 different search weight configurations
- 4 different paper generation strategies
- 4 different answer evaluation scenarios
- 3 different difficulty level filters

### Best Practices
- Proper HTTP methods (GET, POST)
- Proper content types (application/json)
- Proper status codes (200, 400, 422, 500)
- Proper error handling

---

## 🚀 Quick Reference

### Health Check
```
GET /health
Response: {"status": "healthy"}
```

### Ask Endpoint
```
POST /api/v1/ask
Body: {"question": "...", "hybrid_search": {...}}
Response: {"answer": "...", "sources": [...]}
```

### Similar Questions
```
POST /api/v1/similar-questions
Body: {"question_text": "...", "top_k": 5, "difficulty": null}
Response: {"questions": [...], "total_found": n}
```

### Generate Paper
```
POST /api/v1/generate-paper
Body: {"year": 2025, "difficulty_distribution": null}
Response: {"paper_id": "...", "questions": [...], "total_marks": 100}
```

### Evaluate Answer
```
POST /api/v1/evaluate-answer
Body: {"question_text": "...", "student_answer": "...", "question_id": null}
Response: {"feedback": {...}, "match_percentage": 75, "confidence": 0.75}
```

---

## 🔐 Security Notes

- ✅ No API keys stored in collection
- ✅ Base URL uses variable (easy to change)
- ✅ All requests use standard authentication headers
- ✅ Ready for API key injection later

---

## 📝 Customization Ideas

### 1. Add Authentication
```javascript
// Pre-request Script
pm.addHeader({key: "Authorization", value: "Bearer " + pm.globals.get("token")});
```

### 2. Add Response Assertions
```javascript
// Tests tab
pm.test("Response time < 500ms", () => pm.expect(pm.response.responseTime).to.be.below(500));
```

### 3. Create Collection Runner Script
```javascript
// Run all requests with 1-second delay
```

### 4. Export Results
```javascript
// Save all responses to file
```

---

## ✨ Features Included

✅ **Complete API Coverage**
- All 4 main endpoints
- All variations
- Health checks
- Metrics monitoring

✅ **Production Ready**
- Proper HTTP methods
- Proper error codes
- Proper headers
- Proper validation

✅ **Easy to Learn**
- Clear naming
- Good documentation
- Example responses
- Step-by-step guide

✅ **Easy to Modify**
- Pre-built templates
- Change any field easily
- Copy requests for variations
- Reusable across tests

✅ **Well Organized**
- Grouped by endpoint
- Grouped by feature
- Clear structure
- Easy navigation

---

## 🎯 Next Steps

### Immediate (Now)
1. Download Postman
2. Import collection
3. Set base_url
4. Send Health Check

### Soon (Next Hour)
1. Try all 4 endpoints
2. Compare different weights
3. Generate papers
4. Evaluate answers

### Later (Today)
1. Read POSTMAN_GUIDE.md
2. Explore all requests
3. Monitor /metrics
4. Plan next tests

---

## 📞 Support Resources

| Document | Purpose |
|----------|---------|
| POSTMAN_QUICK_START.md | Quick reference + troubleshooting |
| POSTMAN_GUIDE.md | Detailed guide + advanced usage |
| README.md | API documentation |
| TESTING_GUIDE.md | Backend testing guide |

---

## 🎉 You're All Set!

**What You Have**:
✅ 17 pre-built requests
✅ All endpoints covered
✅ Example responses
✅ Testing guidelines
✅ Troubleshooting guide

**What You Can Do**:
✅ Test immediately (no setup needed)
✅ Compare search algorithms
✅ Generate test papers
✅ Evaluate student answers
✅ Monitor performance

**Time to First Test**: **2 minutes** ⏱️

---

## 📂 Files Location

```
ExamSmith/
├── ExamSmith-Retrieval-API.postman_collection.json  ← Main file
├── POSTMAN_QUICK_START.md                           ← Quick start
├── POSTMAN_GUIDE.md                                 ← Full guide
└── backend/retrival/                                ← Backend code
```

---

## 🚀 Ready to Test!

```bash
# What to do:
1. Download Postman from postman.com
2. Import: ExamSmith-Retrieval-API.postman_collection.json
3. Set {{base_url}} = http://localhost:8000
4. Click Health Check → Send
5. View response → Should say "healthy"
6. Explore other requests!

# Expected Time: 5 minutes total

Questions? See POSTMAN_QUICK_START.md

Happy Testing! 🎉
```

---

**Version**: 1.0
**Created**: 2026-01-20
**Format**: Postman Collection v2.1
**Requests**: 17
**Status**: ✅ Production Ready
