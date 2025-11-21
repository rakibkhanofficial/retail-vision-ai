#!/bin/bash

echo "🔍 Retail Vision AI - Smart Product Detection - Setup Verification"
echo "=================================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo -n "Checking Docker... "
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running${NC}"
    echo "  Please start Docker Desktop"
    exit 1
fi

# Check Docker Compose
echo -n "Checking Docker Compose... "
if docker compose version > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker Compose is available${NC}"
else
    echo -e "${RED}✗ Docker Compose not found${NC}"
    exit 1
fi

# Check .env file
echo -n "Checking .env file... "
if [ -f .env ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
    
    # Check for Gemini API key
    if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
        echo -e "${YELLOW}  ⚠️  Warning: GEMINI_API_KEY not configured${NC}"
        echo "     Get your key from: https://makersuite.google.com/app/apikey"
    elif grep -q "GEMINI_API_KEY=" .env && ! grep -q "GEMINI_API_KEY=$" .env; then
        echo -e "${GREEN}  ✓ GEMINI_API_KEY is configured${NC}"
    else
        echo -e "${YELLOW}  ⚠️  GEMINI_API_KEY appears to be empty${NC}"
    fi
else
    echo -e "${YELLOW}✗ .env file not found${NC}"
    echo "  Creating from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}  ⚠️  Please edit .env and add your GEMINI_API_KEY${NC}"
fi

# Check ports
echo ""
echo "Checking required ports..."

check_port() {
    PORT=$1
    NAME=$2
    
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}  ⚠️  Port $PORT ($NAME) is already in use${NC}"
        return 1
    else
        echo -e "${GREEN}  ✓ Port $PORT ($NAME) is available${NC}"
        return 0
    fi
}

check_port 3000 "Frontend"
check_port 8000 "Backend"
check_port 5432 "Database"

# Check file structure
echo ""
echo "Checking project structure..."

check_file() {
    FILE=$1
    DESC=$2
    
    if [ -f "$FILE" ]; then
        echo -e "${GREEN}  ✓ $DESC${NC}"
    else
        echo -e "${RED}  ✗ $DESC not found${NC}"
    fi
}

check_file "docker-compose.yml" "docker-compose.yml"
check_file "backend/Dockerfile" "Backend Dockerfile"
check_file "backend/app/main.py" "Backend main.py"
check_file "backend/requirements.txt" "Backend requirements.txt"
check_file "frontend/Dockerfile" "Frontend Dockerfile"
check_file "frontend/package.json" "Frontend package.json"
check_file "frontend/src/app/page.tsx" "Frontend page.tsx"

echo ""
echo "==========================================="
echo "Summary:"
echo ""

if [ -f .env ] && ! grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
    echo -e "${GREEN}✓ System is ready to start!${NC}"
    echo ""
    echo "Run: ${GREEN}docker compose up --build${NC}"
    echo "Or:  ${GREEN}./start.sh${NC}"
    echo "For development: ${GREEN}./dev-start.sh${NC}"
else
    echo -e "${YELLOW}⚠️  Please configure GEMINI_API_KEY in .env first${NC}"
    echo ""
    echo "1. Get API key from: https://makersuite.google.com/app/apikey"
    echo "2. Edit .env and paste your key"
    echo "3. Run: docker compose up --build"
fi