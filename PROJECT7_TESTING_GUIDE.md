# Project 7: Testing Guide & Examples

## 🧪 Complete Testing Flow

This guide walks through testing the RAG implementation step-by-step.

---

## Prerequisites

### 1. Ensure Servers are Running

**Backend:**
```bash
cd /Users/ferozshaik/Desktop/Tothu/backend
../venv/bin/python -m uvicorn main:app --reload --port 8001
```

**Frontend:**
```bash
cd /Users/ferozshaik/Desktop/Tothu/frontend
npm run dev
```

### 2. Create Test Documents

Create sample PDFs for testing:

**test_document.txt** (already exists in workspace):
```
This is a test document about artificial intelligence.
AI is transforming how we work and live.
Machine learning is a subset of AI.
```

---

## Test Scenario 1: Basic PDF Upload & Query

### Step 1: Login
1. Go to http://localhost:3000/login
2. Login with your credentials
3. Verify you're redirected to chat

### Step 2: Start New Thread
1. Click "New Chat" in sidebar
2. Send a message: "Hello"
3. AI responds, thread is created

### Step 3: Upload Document
1. Click the 📎 (paperclip) icon
2. Select `test_document.txt`
3. Click "Upload"
4. Wait for success message

**Expected Output:**
```
✅ Document uploaded successfully!

test_document.txt is being processed and will be available shortly.

You can now ask questions about this document.
```

### Step 4: Query Document
Send these messages and verify responses:

**Query 1:** "What is this document about?"
**Expected:** AI mentions artificial intelligence, based on document content

**Query 2:** "What is machine learning according to the document?"
**Expected:** "Machine learning is a subset of AI" (direct from document)

**Query 3:** "What is quantum computing?"
**Expected:** "I cannot find this information in the uploaded document."

---

## Test Scenario 2: Multiple Documents in Same Thread

### Step 1: Create Second Document

Create `document2.txt`:
```
Python is a programming language.
It is widely used for data science and machine learning.
Python has a simple syntax that is easy to learn.
```

### Step 2: Upload to Same Thread
1. Click 📎 again
2. Upload `document2.txt`
3. Wait for success

### Step 3: Query Both Documents

**Query:** "What does the document say about Python?"
**Expected:** AI pulls information from document2.txt

**Query:** "What does the document say about AI?"
**Expected:** AI pulls information from test_document.txt

**Query:** "How are Python and machine learning related?"
**Expected:** AI combines info from both documents

---

## Test Scenario 3: Thread Isolation

### Step 1: Create New Thread
1. Click "New Chat" in sidebar
2. Start new conversation

### Step 2: Query Without Uploading
**Query:** "What is machine learning?"
**Expected:** Normal AI response (NOT from previous documents)

### Step 3: Upload to New Thread
1. Upload a different document
2. Verify it doesn't see documents from first thread

---

## Test Scenario 4: Document Status Check

### Via API

```bash
# Get documents for specific thread
curl -X GET "http://localhost:8001/api/documents/?thread_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "filename": "uuid.txt",
    "original_filename": "test_document.txt",
    "file_size": 150,
    "file_type": "txt",
    "status": "ready",
    "chunk_count": 1,
    "created_at": "2026-01-19T12:00:00"
  }
]
```

---

## Test Scenario 5: Error Handling

### Test 1: Upload Before Starting Chat
1. Try clicking 📎 without starting conversation
**Expected:** Error message asking to start chat first

### Test 2: Invalid File Type
1. Try uploading `.jpg` or `.xlsx`
**Expected:** "Only PDF, TXT, and DOCX files are supported"

### Test 3: File Too Large
1. Try uploading file > 10MB
**Expected:** "File size must be less than 10MB"

### Test 4: Query Outside Document Scope
1. Upload technical document
2. Ask about unrelated topic
**Expected:** "I cannot find this information in the uploaded document."

---

## Test Scenario 6: PDF Processing

### Create Sample PDF

Use this Python script to create test PDF:

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf():
    c = canvas.Canvas("test_report.pdf", pagesize=letter)
    c.drawString(100, 750, "Annual Sales Report 2025")
    c.drawString(100, 730, "")
    c.drawString(100, 710, "Total Revenue: $1.2 Million")
    c.drawString(100, 690, "Growth Rate: 25%")
    c.drawString(100, 670, "Top Product: Widget X")
    c.drawString(100, 650, "Customer Satisfaction: 4.8/5")
    c.save()

create_test_pdf()
```

### Test PDF Upload
1. Upload `test_report.pdf`
2. Query: "What was the total revenue?"
**Expected:** "$1.2 Million"

3. Query: "What is the customer satisfaction score?"
**Expected:** "4.8/5"

---

## Test Scenario 7: Backend Logs Verification

### Check Logs During Upload

**Expected Log Entries:**
```
INFO - Document uploaded: test_document.txt by user user@email.com to thread 5
INFO - Extracting text from test_document.txt
INFO - Chunking text from test_document.txt
INFO - Saving 1 chunks to vector store for thread 5
INFO - Document test_document.txt processed successfully with 1 chunks
```

### Check Logs During RAG Query

**Expected Log Entries:**
```
INFO - Using RAG for user user@email.com in thread 5
INFO - Retrieved 1 chunks for user 1 thread 5
INFO - Sending request to Gemini with 3 messages (RAG: True)
INFO - Successfully received response from Gemini
```

---

## Test Scenario 8: Database Verification

### Check Document Record

```bash
sqlite3 backend/sql_app.db

# View uploaded documents
SELECT id, user_id, thread_id, original_filename, status, chunk_count 
FROM documents;
```

**Expected Output:**
```
1|1|5|test_document.txt|ready|1
```

### Check ChromaDB

```bash
ls -la backend/chroma_db/
```

**Expected:** Directory with collection data

---

## Test Scenario 9: Concurrent Users

### Test Isolation
1. Login as User A, upload doc to Thread 1
2. Login as User B, upload doc to Thread 2
3. User A queries their doc → Success
4. User B queries their doc → Success
5. Verify User A can't see User B's docs

---

## Performance Tests

### Test 1: Large PDF (5-10MB)
1. Upload research paper PDF
2. Measure processing time
**Expected:** 5-15 seconds for embedding generation

### Test 2: Multiple Queries
1. Upload document
2. Send 10 different queries rapidly
**Expected:** All get relevant responses

### Test 3: Multiple Documents
1. Upload 5 documents to same thread
2. Query across all documents
**Expected:** Retrieves most relevant chunks

---

## API Testing with cURL

### 1. Upload Document

```bash
# Get your token from browser dev tools or login
TOKEN="your_jwt_token"

curl -X POST "http://localhost:8001/api/documents/upload?thread_id=5" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_document.txt"
```

### 2. List Documents

```bash
curl -X GET "http://localhost:8001/api/documents/?thread_id=5" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Chat with RAG

```bash
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "What is this document about?",
    "thread_id": 5
  }'
```

### 4. Delete Document

```bash
curl -X DELETE "http://localhost:8001/api/documents/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Python API Client

### Test Script

```python
import requests
import time

BASE_URL = "http://localhost:8001"

# 1. Login
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "test@example.com",
    "password": "password123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Create thread (send first message)
response = requests.post(f"{BASE_URL}/api/chat", 
    headers=headers,
    json={"message": "Hello"}
)
thread_id = response.json()["thread_id"]
print(f"Thread created: {thread_id}")

# 3. Upload document
with open("test_document.txt", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{BASE_URL}/api/documents/upload?thread_id={thread_id}",
        headers=headers,
        files=files
    )
print(f"Upload response: {response.json()}")

# 4. Wait for processing
time.sleep(3)

# 5. Query document
response = requests.post(f"{BASE_URL}/api/chat",
    headers=headers,
    json={
        "message": "What is this document about?",
        "thread_id": thread_id
    }
)
print(f"AI Response: {response.json()['message']}")
```

---

## Troubleshooting Tests

### Issue: "Document processing failed"
**Debug:**
```bash
# Check backend logs
tail -f backend/logs/app.log

# Check if file was saved
ls -la backend/uploads/

# Check ChromaDB
python -c "import chromadb; client = chromadb.PersistentClient(path='backend/chroma_db'); print(client.list_collections())"
```

### Issue: "No relevant chunks found"
**Debug:**
1. Check document status is "ready"
2. Verify chunk_count > 0
3. Check embeddings were created
4. Try rephrasing query

### Issue: RAG not triggering
**Debug:**
```python
# Test RAG service directly
from app.services.rag_service import get_rag_service

rag = get_rag_service()
should_use = rag.should_use_rag(user_id=1, thread_id=5)
print(f"Should use RAG: {should_use}")

chunks = rag.retrieve_relevant_chunks(1, 5, "test query")
print(f"Retrieved {len(chunks)} chunks")
```

---

## Success Checklist

- [ ] Can upload PDF, TXT, DOCX files
- [ ] Documents process in background
- [ ] Status changes from "processing" to "ready"
- [ ] Chunks created and stored in ChromaDB
- [ ] Queries return document-based answers
- [ ] Out-of-scope queries return "cannot find information"
- [ ] Multiple documents work in same thread
- [ ] Thread isolation works (no cross-thread access)
- [ ] Concurrent users don't see each other's docs
- [ ] Delete removes document and embeddings
- [ ] Error messages are user-friendly
- [ ] Logs show RAG activity

---

## Expected Behavior Summary

| Action | Expected Result |
|--------|----------------|
| Upload PDF | Processing starts, status shows in DB |
| Upload before thread | Error: "Start conversation first" |
| Wrong file type | Error: "File type not supported" |
| Query with docs | RAG-based answer with citations |
| Query without docs | Normal AI response |
| Out-of-scope query | "Cannot find this information" |
| New thread | Previous docs not accessible |
| Delete doc | File + embeddings removed |

---

**Last Updated:** January 19, 2026  
**Status:** Ready for testing ✅
