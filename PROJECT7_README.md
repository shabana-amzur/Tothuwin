# Project 7: PDF Upload + RAG-based Chat

## 📋 Overview

This project implements a complete RAG (Retrieval-Augmented Generation) system that allows users to upload PDF, TXT, and DOCX documents and have intelligent conversations based on document content using Google Gemini LLM.

### Key Features

✅ **Document Upload**: Support for PDF, TXT, and DOCX files  
✅ **Thread Isolation**: Documents are scoped per chat thread  
✅ **LangChain Integration**: Professional PDF processing and chunking  
✅ **OpenAI Embeddings**: Uses `text-embedding-3-large` for high-quality embeddings  
✅ **ChromaDB Vector Store**: Persistent vector storage with thread-based collections  
✅ **Semantic Search**: Retrieves most relevant chunks for user queries  
✅ **Grounded Responses**: AI answers ONLY from document content  
✅ **Background Processing**: Async document processing doesn't block UI  
✅ **Security**: Thread-level document isolation per user  

---

## 🏗️ Architecture

### Backend Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── database.py          # Document model with thread_id
│   │   └── document.py          # Document schemas
│   ├── services/
│   │   ├── document_service.py  # PDF processing, chunking, vectorization
│   │   ├── rag_service.py       # Retrieval logic
│   │   └── chat_service.py      # RAG-enhanced chat
│   └── api/
│       ├── documents.py         # Upload/list/delete endpoints
│       └── chat.py              # RAG-aware chat endpoint
├── chroma_db/                   # Vector database storage
└── uploads/                     # Uploaded files storage
```

### Data Flow

```
1. User uploads PDF → 2. Backend saves file → 3. Background task extracts text
    ↓
4. Text split into chunks → 5. Generate embeddings → 6. Store in ChromaDB
    ↓
7. User asks question → 8. Retrieve relevant chunks → 9. Gemini generates answer
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# OpenAI API for embeddings
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-large

# Google Gemini for LLM
GOOGLE_GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=4
```

### Dependencies (requirements.txt)

```txt
# LangChain & RAG
langchain==0.3.14
langchain-google-genai==2.0.9
langchain-openai==0.2.14
langchain-community==0.3.14

# Vector Store
chromadb==0.5.23

# Document Processing
pypdf==5.1.0
python-docx==1.1.2
python-multipart==0.0.9

# Embeddings
openai==1.x.x
```

---

## 🚀 API Endpoints

### 1. Upload Document

**POST** `/api/documents/upload`

Upload a document to a specific thread.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
```
thread_id: integer (required) - Thread ID to attach document to
```

**Body:** `multipart/form-data`
```
file: PDF, TXT, or DOCX file (max 10MB)
```

**Response:**
```json
{
  "id": 1,
  "filename": "abc-123.pdf",
  "original_filename": "mydocument.pdf",
  "file_size": 245678,
  "file_type": "pdf",
  "status": "processing",
  "created_at": "2026-01-19T12:00:00"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8001/api/documents/upload?thread_id=5" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

---

### 2. List Documents

**GET** `/api/documents/`

Get all documents, optionally filtered by thread.

**Query Parameters:**
```
thread_id: integer (optional) - Filter by thread
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "abc-123.pdf",
    "original_filename": "mydocument.pdf",
    "file_size": 245678,
    "file_type": "pdf",
    "status": "ready",
    "chunk_count": 42,
    "created_at": "2026-01-19T12:00:00"
  }
]
```

---

### 3. Delete Document

**DELETE** `/api/documents/{document_id}`

Delete a document and its embeddings.

**Response:**
```json
{
  "message": "Document deleted successfully",
  "document_id": 1
}
```

---

### 4. Chat with RAG

**POST** `/api/chat`

Send a message. If documents exist in the thread, RAG is automatically enabled.

**Request:**
```json
{
  "message": "What is the main topic of the document?",
  "thread_id": 5
}
```

**Response:**
```json
{
  "message": "Based on the document 'mydocument.pdf', the main topic is...",
  "model": "gemini-2.5-flash",
  "thread_id": 5,
  "used_rag": true
}
```

---

## 💻 Frontend Integration

### File Upload Button

The chat UI includes a file upload button (📎 icon) that:
1. Only allows PDF, TXT, DOCX files
2. Validates file size (max 10MB)
3. Requires an active thread before upload
4. Shows upload progress
5. Displays success/error messages

### User Experience

1. **Start a conversation** to create a thread
2. **Click the 📎 button** to select a file
3. **Upload the file** - processing happens in background
4. **Ask questions** about the document
5. AI will answer using ONLY document content

---

## 🔍 RAG Implementation Details

### 1. Document Processing Service

**File:** `backend/app/services/document_service.py`

**Key Functions:**
- `extract_text()` - Extracts text from PDF/DOCX/TXT
- `chunk_text()` - Splits text with RecursiveCharacterTextSplitter
- `save_to_vectorstore()` - Creates embeddings and stores in ChromaDB
- `process_document()` - Orchestrates entire pipeline

**Chunking Strategy:**
```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)
```

### 2. RAG Service

**File:** `backend/app/services/rag_service.py`

**Key Functions:**
- `get_vectorstore_for_thread()` - Get thread-specific vector store
- `retrieve_relevant_chunks()` - Semantic search with similarity scores
- `format_context_for_prompt()` - Formats chunks for LLM
- `should_use_rag()` - Checks if thread has documents

**Retrieval:**
```python
# Performs similarity search
chunks = vectorstore.similarity_search_with_score(query, k=4)
```

### 3. Chat Service Enhancement

**File:** `backend/app/services/chat_service.py`

**RAG Integration:**
```python
# Check if thread has documents
if rag_service.should_use_rag(user_id, thread_id):
    chunks = rag_service.retrieve_relevant_chunks(user_id, thread_id, query)
    context = rag_service.format_context_for_prompt(chunks)
    
    # Add grounding instructions
    system_prompt += context + """
    IMPORTANT:
    1. Answer ONLY based on document content
    2. If info not in documents: "I cannot find this information"
    3. Cite document names
    """
```

---

## 🔒 Security & Isolation

### Thread-Based Isolation

Each thread gets its own ChromaDB collection:
```python
collection_name = f"user_{user_id}_thread_{thread_id}"
```

This ensures:
- Users can only access their own documents
- Documents in Thread A don't appear in Thread B
- No data leakage between threads

### Document Ownership Validation

```python
# Verify thread belongs to user before upload
thread = db.query(ChatThread).filter(
    ChatThread.id == thread_id,
    ChatThread.user_id == current_user.id
).first()
```

---

## 📊 Database Schema

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    thread_id INTEGER,  -- Thread-specific isolation
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    file_path VARCHAR(500),
    file_size INTEGER,
    file_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'processing',
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (thread_id) REFERENCES chat_threads(id)
);
```

---

## 🧪 Testing Locally

### 1. Install Dependencies

```bash
cd /Users/ferozshaik/Desktop/Tothu
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Update Database Schema

```bash
cd backend
python init_db.py
```

### 3. Start Servers

**Backend:**
```bash
cd backend
../venv/bin/python -m uvicorn main:app --reload --port 8001
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Test RAG Flow

1. **Login** to the application
2. **Start a new chat** (creates thread)
3. **Upload a PDF** using the 📎 button
4. **Wait** for "Document uploaded successfully" message
5. **Ask questions** about the document:
   - "What is this document about?"
   - "Summarize the main points"
   - "What does section 3 say?"
6. **Test grounding**: Ask something NOT in the document
   - Expected: "I cannot find this information in the uploaded document."

---

## 📝 Example Request/Response

### Scenario: Upload and Query

**1. Upload Document**
```bash
curl -X POST "http://localhost:8001/api/documents/upload?thread_id=5" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@research_paper.pdf"
```

**2. Chat with RAG**
```bash
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "What methodology was used in this research?",
    "thread_id": 5
  }'
```

**Response:**
```json
{
  "message": "According to research_paper.pdf, the methodology section describes a mixed-methods approach combining quantitative surveys (n=500) with qualitative interviews (n=25). The study used stratified random sampling...",
  "model": "gemini-2.5-flash",
  "thread_id": 5,
  "used_rag": true
}
```

---

## 🚨 Error Handling

### Upload Errors

| Error | Reason | Solution |
|-------|--------|----------|
| "Thread not found" | Invalid thread_id | Start a chat first |
| "File type not supported" | Wrong format | Use PDF/TXT/DOCX only |
| "File too large" | Size > 10MB | Compress or split file |
| "Document processing failed" | Corrupted file | Check file integrity |

### Chat Errors

| Error | Reason | Solution |
|-------|--------|----------|
| "I cannot find this information" | Question outside document scope | Rephrase or provide more context |
| No RAG context | Document still processing | Wait a few seconds |

---

## 📈 Performance Considerations

### Optimization Tips

1. **Chunk Size**: Adjust based on document type
   - Technical docs: 1000 tokens
   - Narrative text: 1500 tokens

2. **Retrieval K**: Balance relevance vs context
   - Simple queries: k=3
   - Complex queries: k=5-6

3. **Embedding Model**: `text-embedding-3-large` provides best quality

4. **Background Processing**: Documents process async - UI remains responsive

---

## 🔄 Migration Guide

If upgrading from previous version:

```bash
# 1. Backup database
cp sql_app.db sql_app.db.backup

# 2. Add thread_id column
sqlite3 sql_app.db "ALTER TABLE documents ADD COLUMN thread_id INTEGER;"

# 3. Restart backend
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'pypdf'"
**Solution:** `pip install pypdf==5.1.0`

### Issue: ChromaDB collection not found
**Solution:** First upload creates collection automatically

### Issue: RAG not working
**Check:**
1. Document status is "ready" (not "processing")
2. Thread ID matches between upload and chat
3. OpenAI API key is valid
4. ChromaDB directory exists and is writable

---

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Google Gemini API](https://ai.google.dev/docs)

---

## ✅ Success Criteria

Project 7 is successfully implemented when:

- [x] Users can upload PDF/TXT/DOCX files
- [x] Documents are processed and chunked correctly
- [x] Embeddings are stored in ChromaDB
- [x] Chat automatically uses RAG when documents exist
- [x] Answers are grounded in document content
- [x] Thread isolation works (documents don't leak)
- [x] Multiple documents per thread supported
- [x] Background processing doesn't block UI
- [x] Proper error handling and logging

---

**Project Status:** ✅ **COMPLETE**

**Implementation Date:** January 19, 2026  
**Backend:** FastAPI + LangChain + ChromaDB  
**Frontend:** Next.js + TypeScript  
**LLM:** Google Gemini 2.5 Flash  
**Embeddings:** OpenAI text-embedding-3-large  
