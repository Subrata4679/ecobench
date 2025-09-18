@echo off
echo Starting EcoBench backend (Simplified Version)...

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Starting simplified FastAPI server...
echo This version uses in-memory storage and mock AI services
echo Access the API at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

uvicorn app.simple_main:app --reload --host 0.0.0.0 --port 8000

pause
