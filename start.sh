#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🇸🇪 Svenska Lären - Starting..."

# Start backend in background
echo "Starting backend on :8003..."
cd "$PROJECT_DIR/backend"
uvicorn main:app --port 8003 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend on :5173..."
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
