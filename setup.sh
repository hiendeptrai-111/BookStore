#!/bin/bash
# Setup script for BookStore Chatbot with Gemini AI

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   BookStore Chatbot with Gemini AI - Automated Setup       ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo -e "\n${BLUE}[1/8] Checking Python...${NC}"
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check Node.js
echo -e "\n${BLUE}[2/8] Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠ Node.js not found. Frontend setup will be skipped.${NC}"
    SKIP_FRONTEND=true
else
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"
fi

# Backend Setup
echo -e "\n${BLUE}[3/8] Setting up Backend...${NC}"
cd backend

# Create venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Installed requirements${NC}"

# Setup .env
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please add your GEMINI_API_KEY to backend/.env${NC}"
    NEED_API_KEY=true
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate > /dev/null 2>&1
echo -e "${GREEN}✓ Database migrations completed${NC}"

# Check .env for API key
if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
    NEED_API_KEY=true
fi

cd ..

# Frontend Setup
if [ "$SKIP_FRONTEND" != "true" ]; then
    echo -e "\n${BLUE}[4/8] Setting up Frontend...${NC}"
    cd frontend
    
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cp .env.example .env
    fi
    
    echo "Installing npm packages..."
    npm install > /dev/null 2>&1
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    
    cd ..
else
    echo -e "\n${BLUE}[4/8] Skipping Frontend Setup${NC}"
fi

# Success message
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✓ Setup Complete!                                         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

# Print next steps
echo -e "\n${BLUE}📋 Next Steps:${NC}"
echo ""
echo -e "1. ${YELLOW}Get Gemini API Key:${NC}"
echo "   - Visit: https://ai.google.dev"
echo "   - Click 'Get API Key' → Create API key"
echo "   - Copy the key"
echo ""
echo -e "2. ${YELLOW}Add API Key to backend/.env:${NC}"
echo "   - Open: backend/.env"
if [ "$NEED_API_KEY" = "true" ]; then
    echo -e "   - Replace: ${RED}GEMINI_API_KEY=your_gemini_api_key_here${NC}"
else
    echo -e "   - API Key already set ✓"
fi
echo "   - With: GEMINI_API_KEY=YOUR_ACTUAL_KEY"
echo ""
echo -e "3. ${YELLOW}Start Backend Server:${NC}"
echo "   - Run: cd backend && python manage.py runserver"
echo "   - Server at: http://localhost:8000/api"
echo ""
if [ "$SKIP_FRONTEND" != "true" ]; then
    echo -e "4. ${YELLOW}Start Frontend Server (in another terminal):${NC}"
    echo "   - Run: cd frontend && npm run dev"
    echo "   - Frontend at: http://localhost:5173"
    echo ""
    echo -e "5. ${YELLOW}Test the Chatbot:${NC}"
    echo "   - Open http://localhost:5173"
    echo "   - Click chat icon and start talking!"
else
    echo -e "4. ${YELLOW}Frontend Setup:${NC}"
    echo "   - Please install Node.js first"
    echo "   - Then run: npm install in frontend/ directory"
fi
echo ""

# Display API key status
if [ "$NEED_API_KEY" = "true" ]; then
    echo -e "${RED}⚠️  IMPORTANT: Don't forget to add GEMINI_API_KEY!${NC}"
fi

echo -e "\n${BLUE}📚 Documentation:${NC}"
echo "   - Full Guide: CHATBOT_QUICKSTART.md"
echo "   - Setup Details: backend/CHATBOT_SETUP.md"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
