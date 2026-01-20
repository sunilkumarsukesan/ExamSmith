@echo off
REM ExamSmith Retrieval Backend - Setup Script for Windows

echo.
echo ============================================================
echo ExamSmith Retrieval Backend - Setup Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    exit /b 1
)

echo [1/4] Python detected:
python --version

REM Create virtual environment
echo.
echo [2/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping...
) else (
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo.
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo [4/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env and configure:
echo    - MONGODB_URI
echo    - GROQ_API_KEY
echo.
echo 2. Ensure MongoDB Atlas indexes are created:
echo    - Textbook: BM25 on 'content', Vector on 'embedding'
echo    - Questions: Vector on 'embedding'
echo.
echo 3. Start the server:
echo    uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 4. Test health check:
echo    curl http://localhost:8000/health
echo.
