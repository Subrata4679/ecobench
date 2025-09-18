@echo off
echo Starting EcoBench backend in development mode...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set environment variables for development
set DATABASE_URL=sqlite:///./ecobench_dev.db
set LLM_PROVIDER=mock
set SECRET_KEY=dev-secret-key-change-in-production
set DEBUG=true
set LOG_LEVEL=DEBUG

echo Environment configured for development mode
echo Database: SQLite (local file)
echo LLM Provider: Mock (no external API needed)
echo.

REM Start the server
echo Starting FastAPI server...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
