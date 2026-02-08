#!/bin/bash

echo "🚀 Starting Bhasha Kahani Development Servers"
echo "============================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}📦 Starting Backend (FastAPI)...${NC}"
echo "   URL: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""

# Start backend in background
cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

echo ""
echo -e "${BLUE}🎨 Starting Frontend (Next.js)...${NC}"
echo "   URL: http://localhost:3000"
echo ""

# Start frontend in background
cd apps/web/my-app && npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅ Both servers are starting!${NC}"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
