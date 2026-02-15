#!/bin/bash
# ExamSmith Retrieval Backend - Setup Script for Linux/macOS

echo ""
echo "============================================================"
echo "ExamSmith Retrieval Backend - Setup Script"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org/"
    exit 1
fi

echo "[1/4] Python detected:"
python3 --version

# Create virtual environment
echo ""
echo "[2/4] Creating virtual environment..."
if [ -d venv ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo ""
echo "[3/4] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "[4/4] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure:"
echo "   - MONGODB_URI"
echo "   - GROQ_API_KEY"
echo ""
echo "2. Ensure MongoDB Atlas indexes are created:"
echo "   - Textbook: BM25 on 'content', Vector on 'embedding'"
echo "   - Questions: Vector on 'embedding'"
echo ""
echo "3. Start the server:"
echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "4. Test health check:"
echo "   curl http://localhost:8000/health"
echo ""
