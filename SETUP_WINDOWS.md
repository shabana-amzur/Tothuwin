# Windows Setup Guide

This guide provides Windows-specific instructions for setting up the Tothu project.

## Prerequisites

1. **Python 3.9+**
   - Download from: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: During installation, check "Add Python to PATH"

2. **Node.js 18+**
   - Download from: https://nodejs.org/
   - Choose the LTS (Long Term Support) version

3. **Git**
   - Download from: https://git-scm.com/download/win
   - Use default settings during installation

4. **Code Editor** (optional but recommended)
   - Visual Studio Code: https://code.visualstudio.com/

## Setup Instructions

### 1. Clone the Repository

Open **Command Prompt** or **PowerShell** and run:

```cmd
git clone https://github.com/shabana-amzur/tothu.git
cd tothu
```

### 2. Create and Activate Virtual Environment

#### Using Command Prompt:
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Using PowerShell:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Note**: If you get an execution policy error in PowerShell, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Backend Dependencies

```cmd
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```cmd
copy .env.example .env
```

Or manually create `.env` with:

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

### 5. Initialize Database

```cmd
cd backend
..\venv\Scripts\python.exe init_db.py
..\venv\Scripts\python.exe create_test_user.py
cd ..
```

This creates a test user:
- Email: `test@example.com`
- Password: `test123`

### 6. Install Frontend Dependencies

```cmd
cd frontend
npm install
cd ..
```

### 7. Start the Servers

You have three options:

#### Option A: Using Batch Script (Command Prompt)
```cmd
start.bat
```

#### Option B: Using PowerShell Script
```powershell
.\start.ps1
```

#### Option C: Manual Start (Two separate windows)

**Window 1 - Backend:**
```cmd
cd backend
..\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
```

**Window 2 - Frontend:**
```cmd
cd frontend
npm run dev
```

## Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs (Swagger UI)

## Common Windows Issues

### Issue 1: "python is not recognized"
**Solution**: Add Python to PATH
1. Search "Environment Variables" in Windows
2. Edit "Path" in System Variables
3. Add Python installation path (e.g., `C:\Users\YourName\AppData\Local\Programs\Python\Python311`)
4. Add Scripts folder (e.g., `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts`)

### Issue 2: "npm is not recognized"
**Solution**: Reinstall Node.js and ensure "Add to PATH" is checked

### Issue 3: PowerShell Execution Policy Error
**Solution**: Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 4: Port Already in Use
**Solution**: Kill the process using the port

Find the process:
```cmd
netstat -ano | findstr :8001
netstat -ano | findstr :3000
```

Kill the process (replace PID with actual process ID):
```cmd
taskkill /PID <PID> /F
```

### Issue 5: Virtual Environment Not Activating
**Solution**: 
- Make sure you're in the project root directory
- Check that `venv\Scripts\activate.bat` exists (Command Prompt)
- Check that `venv\Scripts\Activate.ps1` exists (PowerShell)

## Windows vs macOS Differences

| Component | macOS | Windows |
|-----------|-------|---------|
| Virtual env activation | `source venv/bin/activate` | `venv\Scripts\activate` |
| Python executable | `venv/bin/python` | `venv\Scripts\python.exe` |
| Path separator | `/` | `\` |
| Start script | `./start.sh` | `start.bat` or `.\start.ps1` |
| Script permissions | `chmod +x start.sh` | Not needed |

## Development Workflow

### Daily Workflow
1. Open terminal in project root
2. Activate virtual environment:
   ```cmd
   venv\Scripts\activate
   ```
3. Pull latest changes:
   ```cmd
   git pull
   ```
4. Start servers:
   ```cmd
   start.bat
   ```

### Stopping Servers
- Close the terminal windows running the servers, or
- Press `Ctrl+C` in each terminal window

## Project Structure

```
Tothu/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   ├── main.py          # Backend entry point
│   └── sql_app.db       # SQLite database
├── frontend/            # Next.js frontend
│   ├── app/            # App router pages
│   └── public/         # Static assets
├── venv/               # Python virtual environment
├── .env                # Environment variables
├── requirements.txt    # Python dependencies
├── start.bat           # Windows batch script
└── start.ps1          # Windows PowerShell script
```

## Testing the Setup

1. Login with test credentials:
   - Email: `test@example.com`
   - Password: `test123`

2. Test the chatbot:
   - Type a message and get AI response

3. Test Project 8 (NL2SQL):
   - Go to http://localhost:8001/docs
   - Try endpoint: `/api/nl-to-sql/` with query "How many users?"

## Getting Help

- Check existing documentation: `README_PROJECT3.md`, `PROJECT8_QUICK_START.md`
- View API documentation: http://localhost:8001/docs
- Check backend logs in the terminal window

## Notes

- The SQLite database (`backend/sql_app.db`) works identically on Windows and macOS
- All Python and Node.js code is cross-platform
- Only startup scripts differ between operating systems
- You can safely switch between Windows and macOS by pulling latest code from Git
