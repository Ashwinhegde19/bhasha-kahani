#!/bin/bash

# Bhasha Kahani - Stop Script
# Stops both Backend (API) and Frontend (Web)

echo "🛑 Stopping Bhasha Kahani..."
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
        echo -e "${YELLOW}⚠️  Stopping $name on port $port...${NC}"
        
        # Try graceful kill first
        lsof -ti :$port | xargs kill -15 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if check_port $port; then
            lsof -ti :$port | xargs kill -9 2>/dev/null
            sleep 1
        fi
        
        if check_port $port; then
            echo -e "${RED}❌ Failed to stop $name${NC}"
            return 1
        else
            echo -e "${GREEN}✅ $name stopped${NC}"
            return 0
        fi
    else
        echo -e "${BLUE}ℹ️  $name is not running${NC}"
        return 0
    fi
}

# Kill processes
kill_port 8000 "Backend (API)"
kill_port 3000 "Frontend (Web)"

echo ""
echo -e "${GREEN}🎉 Bhasha Kahani stopped!${NC}"
