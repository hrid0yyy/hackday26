#!/bin/bash

echo "Starting FastAPI Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""

# Run the FastAPI application
echo "Starting FastAPI server..."
echo "Server will be available at http://127.0.0.1:8000"
echo "API documentation at http://127.0.0.1:8000/docs"
echo ""
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
