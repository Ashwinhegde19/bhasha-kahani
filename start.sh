#!/bin/bash

# Bhasha Kahani - Start Script
# Starts both Backend (API) and Frontend (Web)

echo "🚀 Starting Bhasha Kahani..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Function to kill process on port
kill_port() {
    local port=$1
    local name=$2
    
    if check_port $port; then
        echo -e "${YELLOW}⚠️  $name is already running on port $port${NC}"
        echo -e "${BLUE}🛑 Stopping $name...${NC}"
        
        # Try graceful kill first
        lsof -ti :$port | xargs kill -15 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if check_port $port; then
            lsof -ti :$port | xargs kill -9 2>/dev/null
            sleep 1
        fi
        
        if check_port $port; then
            echo -e "${RED}❌ Failed to stop $name on port $port${NC}"
            exit 1
        else
            echo -e "${GREEN}✅ $name stopped${NC}"
        fi
    fi
}

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$PROJECT_ROOT/apps/api"
WEB_DIR="$PROJECT_ROOT/apps/web/my-app"

echo -e "${BLUE}📁 Project root: $PROJECT_ROOT${NC}"
echo ""

# Kill existing processes
echo -e "${BLUE}🔍 Checking for existing processes...${NC}"
kill_port 8000 "Backend (API)"
kill_port 3000 "Frontend (Web)"
echo ""

# Start Backend
echo -e "${BLUE}🟢 Starting Backend (FastAPI)...${NC}"
cd "$API_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment and start backend
source venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${BLUE}⏳ Waiting for backend to start...${NC}"

# Wait for backend to be ready
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend started successfully (PID: $BACKEND_PID)${NC}"
        echo -e "${BLUE}   API: http://localhost:8000${NC}"
        echo -e "${BLUE}   Health: http://localhost:8000/health${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        echo -e "${YELLOW}   Check logs: tail -f /tmp/backend.log${NC}"
        exit 1
    fi
done

echo ""

# Start Frontend
echo -e "${BLUE}🟢 Starting Frontend (Next.js)...${NC}"
cd "$WEB_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found. Installing...${NC}"
    npm install
fi

# Frontend mode:
#   dev  (default): best for local iteration, avoids stale .next artifacts
#   prod           : performs clean build and starts production server
FRONTEND_MODE="${FRONTEND_MODE:-dev}"

if [ "$FRONTEND_MODE" = "prod" ]; then
    echo -e "${BLUE}🏗️  FRONTEND_MODE=prod: running clean build...${NC}"
    rm -rf .next
    if ! npm run build; then
        echo -e "${RED}❌ Frontend build failed${NC}"
        echo -e "${YELLOW}   Check logs: tail -f /tmp/frontend.log${NC}"
        exit 1
    fi
    nohup npm start > /tmp/frontend.log 2>&1 &
else
    echo -e "${BLUE}🛠️  FRONTEND_MODE=dev: starting Next.js dev server...${NC}"
    nohup npm run dev > /tmp/frontend.log 2>&1 &
fi
FRONTEND_PID=$!

echo -e "${BLUE}⏳ Waiting for frontend to start...${NC}"

# Wait for frontend to be ready
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend started successfully (PID: $FRONTEND_PID)${NC}"
        echo -e "${BLUE}   Web: http://localhost:3000${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Frontend failed to start${NC}"
        echo -e "${YELLOW}   Check logs: tail -f /tmp/frontend.log${NC}"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}🎉 Bhasha Kahani is running!${NC}"
echo ""
echo -e "${BLUE}📱 Application URLs:${NC}"
echo -e "   ${GREEN}• Frontend: http://localhost:3000${NC}"
echo -e "   ${GREEN}• Backend:  http://localhost:8000${NC}"
echo -e "   ${GREEN}• API Docs: http://localhost:8000/docs${NC}"
echo -e "   ${GREEN}• Frontend Mode: ${FRONTEND_MODE}${NC}"
echo ""
echo -e "${BLUE}📖 Quick Links:${NC}"
echo -e "   • Stories: http://localhost:3000/stories"
echo -e "   • Play Punyakoti: http://localhost:3000/play/96603cb7-cb25-4466-9e4c-ce929283063d"
echo ""
echo -e "${YELLOW}📝 Log Files:${NC}"
echo -e "   • Backend:  tail -f /tmp/backend.log"
echo -e "   • Frontend: tail -f /tmp/frontend.log"
echo ""
echo -e "${YELLOW}🛑 To stop:${NC}"
echo -e "   ./stop.sh"
echo -e "   or press Ctrl+C"
echo ""
echo -e "${GREEN}Happy storytelling! 🎙️${NC}"

# Keep script running
wait
