@echo off
cd /d "%~dp0"
echo Starting backend server from: %CD%
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
pause
