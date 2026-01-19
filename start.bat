@echo off
REM Start script for Windows Command Prompt
REM This will start both backend and frontend servers

echo Starting Tothu Application (Windows)...

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Start backend server in a new window
echo Starting backend server on http://localhost:8001...
start "Tothu Backend" cmd /k "cd backend && ..\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server in a new window
echo Starting frontend server on http://localhost:3000...
start "Tothu Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ====================================
echo Both servers are starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8001/docs
echo ====================================
echo.
echo Close this window or press Ctrl+C to stop this script.
echo To stop servers, close their respective windows.
pause
