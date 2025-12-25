#!/bin/bash

# Deepy Quick Start Script
# This script starts both the backend and frontend servers

echo "🧠 Starting Deepy..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Start backend in background
echo "🚀 Starting FastAPI backend on port 8000..."
cd backend
./venv/bin/python main.py &
BACKEND_PID=$!
cd ..


# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Next.js frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Deepy is running!"
echo ""
echo "📊 Backend:  http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
