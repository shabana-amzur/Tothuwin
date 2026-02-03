# Tothu - AI Chat Application

A comprehensive AI-powered chat application with multiple features including document Q&A, Excel analysis, SQL queries, and image validation.

## 🌟 Features

### 1. **Multi-Model Chat**
- **Gemini**: Standard chat with RAG (Retrieval-Augmented Generation) support
- **Agent**: ReAct pattern with tools (calculator, Wikipedia)
- **MCP Style Agent**: Advanced Planner-Selector-Executor-Synthesizer pattern
- **N8N Multi-Agent**: Workflow-based multi-agent system

### 2. **Image Q&A**
- Upload medicine/prescription images
- Ask questions about images using Gemini Vision API
- Supported by Gemini, Agent, and MCP Style models

### 3. **Document Analysis**
- Upload PDF, TXT, DOCX files
- Ask questions about document content
- RAG-powered answers with context

### 4. **Excel Analysis**
- Upload XLSX, XLS, CSV files
- Natural language queries on spreadsheet data
- AI-powered data insights

### 5. **SQL Query Generator**
- Convert natural language to SQL
- Database schema integration
- Query execution and results

### 6. **Image Validation**
- Validate invoices, receipts, ID cards
- AI-powered document verification
- Demo mode available (no API required)

### 7. **Tic-Tac-Toe Game**
- Play against AI
- Interactive game board

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Gemini API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Tothu
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Install dependencies**

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Frontend:
```bash
cd frontend
npm install
```

4. **Start the application**

Option 1 - Using start scripts:
```bash
# On macOS/Linux
./start_all.sh

# On Windows
start_all.bat
```

Option 2 - Manual start:

Backend (Terminal 1):
```bash
cd backend
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Frontend (Terminal 2):
```bash
cd frontend
npm run dev
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## 📁 Project Structure

```
Tothu/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   └── main.py          # Entry point
├── frontend/            # Next.js frontend
│   ├── app/
│   │   ├── components/  # React components
│   │   ├── contexts/    # Context providers
│   │   └── page.tsx     # Main page
│   └── package.json
├── uploads/             # File uploads
├── venv/               # Python virtual environment
├── .env                # Environment variables
└── requirements.txt    # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Google Gemini API
GOOGLE_API_KEY=your_gemini_api_key

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# Database
DATABASE_URL=sqlite:///./backend/sql_app.db

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# N8N (optional)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/multi-agent
```

## 🎯 Usage

### Chat Interface
1. Select a model from the dropdown (Gemini, Agent, MCP Style, N8N)
2. Type your message or question
3. Upload files (documents/images) if needed
4. Get AI-powered responses

### Image Q&A
1. Click the file upload button
2. Select an image (medicine, prescription, etc.)
3. Click "Upload"
4. Ask questions about the image

### Excel Analysis
1. Upload an Excel/CSV file
2. File will be processed automatically
3. Ask natural language questions about your data
4. Get insights and answers

### Image Validation
1. Click "Image Validation" in sidebar
2. Choose document type (Invoice, Receipt, ID Card)
3. Upload image or use Demo mode
4. View validation results

## 🛠️ Development

### Backend Development
```bash
cd backend
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📦 Technologies Used

### Backend
- FastAPI - Web framework
- SQLAlchemy - ORM
- LangChain - LLM framework
- Google Gemini - AI models
- ChromaDB - Vector database
- Python 3.9+

### Frontend
- Next.js 14 - React framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- React Markdown - Markdown rendering

## 🔐 Authentication

- Google OAuth integration
- JWT token-based authentication
- Secure session management

## 📝 API Documentation

Access the interactive API documentation at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- LangChain for LLM orchestration
- FastAPI for backend framework
- Next.js for frontend framework

## 📞 Support

For issues and questions, please open an issue on GitHub.
