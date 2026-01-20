# Installation Notes - Windows Setup

## Installation Summary

**Date:** January 20, 2026

### ✅ Successfully Installed

#### Frontend Dependencies
- **493 npm packages** installed successfully via `npm install` in the frontend directory
- No vulnerabilities found

#### Python Dependencies (Backend)
Most Python packages were installed successfully. Total: **120+ packages**

**Core Dependencies:**
- FastAPI 0.115.6 (Web Framework)
- Uvicorn 0.34.0 (ASGI Server)
- SQLAlchemy 2.0.36 (ORM)
- Alembic 1.14.0 (Database migrations)
- Supabase 2.10.0
- psycopg2-binary 2.9.10 (PostgreSQL adapter)

**AI/ML Dependencies:**
- Google Generative AI 0.8.3 (Gemini API)
- LangChain 0.3.14
- LangChain Google GenAI 2.0.9
- LangChain OpenAI 0.2.14
- LangChain Community 0.3.14
- OpenAI 1.109.1
- TikToken 0.12.0 (Token counting)

**Document Processing:**
- pypdf 5.1.0 (PDF processing)
- python-docx 1.1.2 (DOCX processing)
- python-magic 0.4.27 (File type detection)

**Authentication & Security:**
- PyJWT 2.10.1
- python-jose 3.3.0 (with cryptography)
- passlib 1.7.4 (with bcrypt)
- cryptography 44.0.0
- Authlib 1.3.2
- itsdangerous 2.2.0

**Data Processing:**
- pandas 2.2.3
- numpy 2.4.1

**Development Tools:**
- pytest 8.3.4
- pytest-asyncio 0.24.0
- black 24.10.0 (Code formatter)
- flake8 7.1.1 (Linter)
- mypy 1.14.1 (Type checker)
- ipython 8.30.0

**Other Important Packages:**
- email-validator 2.2.0
- python-multipart 0.0.9 (File uploads)
- python-dotenv 1.2.1 (Environment variables)
- pydantic 2.12.5
- pydantic-settings 2.12.0
- requests 2.32.3

### ⚠️ Not Installed (Requires C++ Build Tools)

**ChromaDB 0.5.23** - Vector database for RAG functionality
- Reason: Requires Microsoft Visual C++ 14.0+ for compilation
- Dependency: `chroma-hnswlib` cannot build on Windows without C++ build tools

## Impact Assessment

### What Works Without ChromaDB:
✅ **Core Functionality:**
- FastAPI backend server
- User authentication and authorization
- Database operations (SQLite/PostgreSQL)
- Google Gemini AI integration
- OpenAI integration
- LangChain chat functionality
- Document upload (PDF, DOCX)
- Natural Language to SQL (NL2SQL) features
- Image generation
- OAuth authentication
- Thread management
- All API endpoints (except RAG-specific ones)

### What Requires ChromaDB:
❌ **RAG (Retrieval Augmented Generation) Features:**
- Document vector storage
- Semantic search in uploaded documents
- Context-aware responses based on uploaded documents
- Document embeddings

## Solutions for ChromaDB

### Option 1: Install Microsoft C++ Build Tools (Recommended for Full Features)
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer
3. Select "Desktop development with C++"
4. Install (~6GB disk space required)
5. After installation, run:
   ```powershell
   C:/Users/Shabana/Desktop/Tothu/.venv/Scripts/python.exe -m pip install chromadb==0.5.23
   ```

### Option 2: Use Alternative Vector Database
Replace ChromaDB with:
- **Pinecone** (Cloud-based, no local dependencies)
- **Weaviate** (Docker-based)
- **Qdrant** (Python-native, lighter alternative)

### Option 3: Skip RAG Features
Continue development without RAG functionality. Most of the application works fine without it.

## Files Modified
- `requirements.txt` - Removed duplicate `python-multipart==0.0.20` entry

## Next Steps

1. **Start the Backend Server:**
   ```powershell
   cd backend
   ..\\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
   ```

2. **Start the Frontend Server:**
   ```powershell
   cd frontend
   npm run dev
   ```

3. **Or use the startup scripts:**
   ```powershell
   # Option 1: PowerShell script
   .\start.ps1
   
   # Option 2: Batch script
   start.bat
   ```

4. **Access the Application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs

5. **Test Login:**
   - Email: `test@example.com`
   - Password: `test123`

## Environment Setup Required

Create a `.env` file in the project root with:
```
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your_secret_key_here
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

Get API keys from:
- Google AI: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys

## Database Initialization

Before first run, initialize the database:
```powershell
cd backend
..\\.venv\Scripts\python.exe init_db.py
..\\.venv\Scripts\python.exe create_test_user.py
cd ..
```

## Troubleshooting

### If you encounter import errors related to chromadb:
Comment out or remove chromadb-related imports in:
- `backend/app/services/rag_service.py`
- Any file importing from `chromadb`

The application should still run without RAG features.

### Port conflicts:
```cmd
# Find process using port
netstat -ano | findstr :8001
netstat -ano | findstr :3000

# Kill process (replace PID with actual ID)
taskkill /PID <PID> /F
```

## Package Versions Summary
See the full list above or run:
```powershell
C:/Users/Shabana/Desktop/Tothu/.venv/Scripts/python.exe -m pip list
```
