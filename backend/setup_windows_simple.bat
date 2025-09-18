@echo off
echo Setting up EcoBench backend on Windows (simplified)...

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install core dependencies first
echo Installing core dependencies...
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install sqlalchemy==2.0.23
pip install alembic==1.12.1
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0
pip install python-multipart==0.0.6
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4
pip install httpx==0.25.2
pip install aiofiles==23.2.1
pip install prometheus-fastapi-instrumentator==6.1.0
pip install prometheus-client==0.19.0
pip install structlog==23.2.0

REM Install testing dependencies
echo Installing testing dependencies...
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1
pip install pytest-cov==4.1.0

REM Install PDF processing (skip problematic ones for now)
echo Installing PDF processing dependencies...
pip install PyPDF2==3.0.1
pip install pdfminer.six==20221105

REM Install ML dependencies (CPU versions for Windows)
echo Installing ML dependencies...
pip install numpy==1.24.4
pip install scikit-learn==1.3.2
pip install pandas==2.1.4
pip install openai==1.3.7

REM Skip database dependencies for now (PostgreSQL setup needed separately)
echo.
echo Core setup complete!
echo.
echo Note: Skipped some dependencies that require additional Windows setup:
echo - PostgreSQL with pgvector (install separately)
echo - Pillow (for image processing)
echo - PyTorch and transformers (large downloads)
echo.
echo To start the backend server:
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
pause
