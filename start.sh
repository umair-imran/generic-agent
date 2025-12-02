#!/bin/bash

# Simple startup script for Hospitality Bot
# Runs both the FastAPI server and LiveKit agent

set -e

echo "🚀 Starting Hospitality Bot..."

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "⚠️  Warning: .env.local not found. Please create it from .env.local.example"
    echo "   Some features may not work without proper configuration."
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $API_PID $AGENT_PID 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Start FastAPI server in background
echo "📡 Starting FastAPI server..."
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "   FastAPI server started (PID: $API_PID)"
echo "   API available at: http://localhost:8000"
echo "   API docs at: http://localhost:8000/docs"

# Wait a bit for API to start
sleep 2

# Start LiveKit agent in background
echo "🤖 Starting LiveKit agent..."
python entrypoint.py dev &
AGENT_PID=$!
echo "   LiveKit agent started (PID: $AGENT_PID)"

echo ""
echo "✅ Both services are running!"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait

