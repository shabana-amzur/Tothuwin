# PROJECT 3: RAG (Retrieval-Augmented Generation) WITH DOCUMENT UPLOAD

## 🎯 Goal
Enable users to upload documents (PDF, TXT, DOCX) and ask questions based on their content using RAG.

## 📋 Features to Implement

### Backend
1. **File Upload API**
   - POST `/api/documents/upload` - Upload documents
   - GET `/api/documents` - List user's documents
   - DELETE `/api/documents/{id}` - Delete a document

2. **Document Processing**
   - Extract text from PDF, TXT, DOCX files
   - Split documents into chunks
   - Generate embeddings
   - Store in vector database

3. **Vector Database**
   - Use ChromaDB for local vector storage
   - Store document chunks with embeddings
   - Link documents to users

4. **RAG Implementation**
   - Retrieve relevant chunks based on user query
   - Augment chat prompt with retrieved context
   - Generate response using Gemini with context

### Frontend
1. **Document Management UI**
   - File upload component with drag-and-drop
   - Document list view
   - Delete documents

2. **Enhanced Chat**
   - Show which documents are being used
   - Display source information in responses

## 🔧 Tech Stack
- **Document Processing**: `langchain-community`, `pypdf`, `python-docx`, `python-magic`
- **Vector Database**: `chromadb`
- **Embeddings**: Google Gemini embeddings
- **File Storage**: Local filesystem + database records

## 📁 New Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── documents.py      # Document upload/management
│   │   └── ...
│   ├── models/
│   │   └── document.py        # Document model
│   ├── services/
│   │   ├── document_service.py  # Document processing
│   │   └── rag_service.py       # RAG implementation
│   └── uploads/               # Uploaded files
│
frontend/
├── app/
│   ├── documents/
│   │   └── page.tsx           # Document management
│   └── components/
│       └── FileUpload.tsx     # Upload component
```

## 🚀 Implementation Steps
1. Install required packages
2. Create document model and database table
3. Implement file upload endpoint
4. Add document processing service
5. Set up ChromaDB vector store
6. Implement RAG service
7. Build frontend upload UI
8. Update chat to use RAG

---

**Status**: 🚧 Starting Implementation
