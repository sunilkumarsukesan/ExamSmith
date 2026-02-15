#!/bin/bash
# ExamSmith Development Setup Guide

echo "🚀 ExamSmith Development Setup"
echo "================================"
echo ""

# Check if Python is installed
echo "1️⃣ Checking Python..."
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.13+"
    exit 1
fi
python --version

# Check if Node.js is installed
echo ""
echo "2️⃣ Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js"
    exit 1
fi
node --version

# Install backend dependencies
echo ""
echo "3️⃣ Installing Backend Dependencies..."
cd backend/retrival
pip install -r requirements.txt
cd ../..

# Install frontend dependencies
echo ""
echo "4️⃣ Installing Frontend Dependencies..."
cd Frontend
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 To run the application:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend/retrival"
echo "  python main.py"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd Frontend"
echo "  npm run dev"
echo ""
echo "🌐 Frontend will be at: http://localhost:5173"
echo "🔌 Backend API will be at: http://localhost:8000/api/v1"
echo "📊 API Docs: http://localhost:8000/docs"
