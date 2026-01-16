# ExamSmith Ingestion Pipeline - Execution Flow

## Overview
Complete flow for extracting textbook data and injecting it into MongoDB through the ExamSmith API.

---

## 🚀 Quick Start Guide

### Step 1: Start the Server

Open **PowerShell** and run:

```powershell
cd "s:\AI TL\VS Projects\ExamSmith"
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

✅ Server is now running on `http://localhost:8000`

---

### Step 2: Extract Textbook Data

Open a **new PowerShell terminal** and run:

```powershell
cd "s:\AI TL\VS Projects\ExamSmith"
python data/extraction/extract_10_english_textbook.py
```

**Expected Output:**
```
📖 Extracting English textbook data...
✓ Extraction complete: book_complete.json created
   📊 Total documents: 5118
   📁 File location: data/extractionOutput/book_complete.json
```

✅ JSON file is now ready at: `data/extractionOutput/book_complete.json`

---

### Step 3: Send to Ingestion API

You have **two options**:

#### **Option A: Using Postman (Recommended)**
1. Import the Postman collection: `ExamSmith-Ingestion-API.postman_collection.json`
2. Go to **"FILE UPLOAD - Upload JSON File"** request
3. Select `data/extractionOutput/book_complete.json` in the file field
4. Click **Send**
5. Copy the `job_id` from the response
6. Use the **"3. Check Status - File Upload"** request to monitor progress

#### **Option B: Using cURL**
```bash
curl -X POST "http://localhost:8000/ingest/file" \
  -F "file=@data/extractionOutput/book_complete.json"
```

#### **Option C: Using Python**
```python
import requests

with open('data/extractionOutput/book_complete.json', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/ingest/file', files=files)
    print(response.json())
```

---

## 📊 Complete Execution Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXAMSMITH INGESTION PIPELINE                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────┐
│  PHASE 1: SERVER INITIALIZATION      │
└──────────────────────────────────────┘
                  │
                  ▼
     ┌─────────────────────────┐
     │  PowerShell Terminal 1  │
     │  > uvicorn start server │
     │  Port: 8000             │
     │  Status: RUNNING ✓      │
     └─────────────────────────┘
                  │
                  │ (Keep this terminal open)
                  │
                  ▼
┌──────────────────────────────────────┐
│  PHASE 2: DATA EXTRACTION            │
└──────────────────────────────────────┘
                  │
                  ▼
     ┌─────────────────────────┐
     │  PowerShell Terminal 2  │
     │  > python extract_10... │
     │  Input: English Textbook│
     └─────────────────────────┘
                  │
                  ▼
     ┌─────────────────────────────────┐
     │  Extract Data from Textbook     │
     │  • Parse content                │
     │  • Generate metadata            │
     │  • Normalize format             │
     └─────────────────────────────────┘
                  │
                  ▼
     ┌─────────────────────────────────┐
     │  📁 Output JSON File Created    │
     │  book_complete.json             │
     │  📊 5,118 documents             │
     │  💾 Located: data/extractionOut │
     └─────────────────────────────────┘
                  │
                  │
                  ▼
┌──────────────────────────────────────┐
│  PHASE 3: API INGESTION              │
└──────────────────────────────────────┘
                  │
                  ▼
     ┌─────────────────────────────────┐
     │  POST /ingest/file              │
     │  http://localhost:8000/ingest/  │
     │  file                           │
     │  (Upload: book_complete.json)   │
     └─────────────────────────────────┘
                  │
                  ▼
     ┌─────────────────────────────────┐
     │  ✅ Response: 200 OK            │
     │  {                              │
     │    "job_id": "uuid...",         │
     │    "status": "pending",         │
     │    "created_at": "2026-01-16"   │
     │  }                              │
     └─────────────────────────────────┘
                  │
                  │ (Copy job_id for monitoring)
                  │
                  ▼
┌──────────────────────────────────────┐
│  PHASE 4: INGESTION PIPELINE         │
└──────────────────────────────────────┘

     ┌────────────────────────────────────────────────┐
     │  [STEP 1/6] 🔍 DEDUPLICATION                   │
     │  Input: 5,118 documents                        │
     │  Output: Content hashes added                  │
     └────────────────────────────────────────────────┘
                        │
                        ▼
     ┌────────────────────────────────────────────────┐
     │  [STEP 2/6] 🧠 EMBEDDING (Batch by 32)        │
     │  API: Mistral AI                               │
     │  Model: mistral-embed                          │
     │  Progress: [████████░░] 50% | ⏳ pending       │
     └────────────────────────────────────────────────┘
                        │
                        ▼
     ┌────────────────────────────────────────────────┐
     │  [STEP 3/6] 📝 PREPARATION                     │
     │  • Add timestamps (created_at, updated_at)    │
     │  • Normalize structure                         │
     │  • Ready for MongoDB                           │
     └────────────────────────────────────────────────┘
                        │
                        ▼
     ┌────────────────────────────────────────────────┐
     │  [STEP 4/6] 💾 MONGODB INJECTION              │
     │  Operation: Bulk Upsert                        │
     │  • New Docs (Upserted): 3,245                 │
     │  • Updated Docs: 1,873                        │
     │  • Total: 5,118/5,118 ✓                       │
     └────────────────────────────────────────────────┘
                        │
                        ▼
     ┌────────────────────────────────────────────────┐
     │  [STEP 5/6] ⚠️  FAILURE HANDLING               │
     │  Failed Records: 0                             │
     │  Status: No failures logged                    │
     └────────────────────────────────────────────────┘
                        │
                        ▼
     ┌────────────────────────────────────────────────┐
     │  [STEP 6/6] ✅ COMPLETION                      │
     │  Status: COMPLETED                             │
     │  Duration: ~2-3 minutes (depends on API)      │
     └────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────┐
│  PHASE 5: MONITORING & VERIFICATION  │
└──────────────────────────────────────┘
                  │
                  ▼
     ┌─────────────────────────────────┐
     │  GET /ingest/status/{job_id}    │
     │  http://localhost:8000/ingest/  │
     │  status/{job_id}                │
     └─────────────────────────────────┘
                  │
                  ▼
     ┌─────────────────────────────────┐
     │  📊 Status Response:            │
     │  {                              │
     │    "job_id": "...",             │
     │    "status": "completed",       │
     │    "total_records": 5118,       │
     │    "processed_records": 5118,   │
     │    "failed_records": 0,         │
     │    "progress_percent": 100.0    │
     │  }                              │
     └─────────────────────────────────┘
                  │
                  ▼
     ┌─────────────────────────────────┐
     │  ✅ INGESTION COMPLETE!         │
     │  All documents in MongoDB       │
     │  Ready for querying             │
     └─────────────────────────────────┘
                  │
                  ▼
           📦 MONGODB
        (Collection: english)
     (Database: 10_books)
  ✅ 5,118 documents stored

```

---

## 🔍 Console Output Examples

### Server Start
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
2026-01-16 21:33:04,740 - src.main - INFO - ExamSmith Ingestion Service starting...
```

### During Embedding
```
🧠 EMBEDDING [Batch 45/160] [███████░░░░░░] ⏳ 32 pending
✅ BATCH SUCCESS [Batch 45/160] 📊 1440/5118 completed | ⏳ 3678 pending
```

### MongoDB Injection
```
💾 MONGODB INJECTION START - Total documents to inject: 5118
✅ MONGODB INJECTION SUCCESS
   📤 New Documents (Upserted): 3245
   🔄 Updated Documents: 1873
   📊 Total Injected: 5118/5118
🎉 INGESTION COMPLETE - All 5118 documents embedded successfully!
```

---

## 📋 Checklist Before Starting

- [ ] MongoDB URI configured in `.env`
- [ ] Mistral API Key configured in `.env`
- [ ] Python 3.13+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Port 8000 is available
- [ ] Textbook data file exists in data/extraction/

---

## ⚙️ Configuration Files

**Location:** `s:\AI TL\VS Projects\ExamSmith\.env`

```env
MONGODB_URI=mongodb+srv://admin:admin@examsmith.0fp2rqj.mongodb.net/?appName=examSmith
MONGODB_DB_NAME=10_books
MONGODB_COLLECTION_NAME=english

MISTRAL_API_KEY=wFEnKDQVOfgwDyk1i34piTl9mFRILJ62
MISTRAL_EMBEDDING_MODEL=mistral-embed

API_HOST=0.0.0.0
API_PORT=8000
BATCH_SIZE=32
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change `API_PORT` in `.env` or kill existing process |
| MongoDB connection failed | Verify `MONGODB_URI` and network access |
| Mistral API errors | Check `MISTRAL_API_KEY` and rate limits |
| Encoding errors with emoji | Already fixed - UTF-8 logging configured |
| Large file timeouts | Increase `EMBEDDING_TIMEOUT` in `.env` |

---

## 📞 Support

For issues or questions:
1. Check the logs in `logs/ingestion.log`
2. Use the status endpoint to check job progress
3. Review failed records in `data/failed_records.json`

---

**Last Updated:** January 16, 2026
**Version:** 1.0.0
