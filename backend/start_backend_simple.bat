@echo off
cd /d "%~dp0"
echo Starting backend server...
call "..\..venv\Scripts\activate.bat"
python -m uvicorn main:app --port 8001
pause
