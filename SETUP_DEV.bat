@echo off
REM ExamSmith Development Setup Guide for Windows

echo.
echo ========================================
echo ExamSmith Development Setup
echo ========================================
echo.

REM Check if Python is installed
echo 1^) Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python not found. Please install Python 3.13+
    pause
    exit /b 1
)
python --version

REM Check if Node.js is installed
echo.
echo 2^) Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Node.js not found. Please install Node.js
    pause
    exit /b 1
)
node --version

REM Install backend dependencies
echo.
echo 3^) Installing Backend Dependencies...
cd backend\retrival
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo X Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..\..

REM Install frontend dependencies
echo.
echo 4^) Installing Frontend Dependencies...
cd Frontend
call npm install
if %errorlevel% neq 0 (
    echo X Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo TO RUN THE APPLICATION:
echo.
echo Terminal 1 - Backend:
echo   cd backend\retrival
echo   python main.py
echo.
echo Terminal 2 - Frontend:
echo   cd Frontend
echo   npm run dev
echo.
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000/api/v1
echo API Docs: http://localhost:8000/docs
echo.
pause
