@echo off
REM BookStore Chatbot with Gemini AI - Setup Script for Windows

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   BookStore Chatbot with Gemini AI - Automated Setup
echo ============================================================
echo.

REM Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ^/ Python %PYTHON_VERSION% found

REM Backend Setup
echo.
echo [2/6] Setting up Backend...
cd backend

REM Create venv
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat
echo ^/ Virtual environment activated

REM Install requirements
echo Installing Python packages...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)
echo ^/ Installed requirements

REM Setup .env
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env >nul
    echo WARNING: Please add GEMINI_API_KEY to backend\.env
    set NEED_API_KEY=1
)

REM Run migrations
echo Running database migrations...
python manage.py migrate >nul 2>&1
echo ^/ Database migrations completed

cd ..

REM Frontend Setup
echo.
echo [3/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Node.js not found. Frontend setup skipped.
    echo Please install Node.js from https://nodejs.org
    goto SKIP_FRONTEND
)

echo [4/6] Setting up Frontend...
cd frontend

if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env >nul
)

echo Installing npm packages...
call npm install >nul 2>&1
if errorlevel 1 (
    echo WARNING: npm install had issues. Check network connection.
)
echo ^/ Frontend dependencies installed

cd ..

:SKIP_FRONTEND
echo.
echo ============================================================
echo   SETUP COMPLETE!
echo ============================================================
echo.
echo NEXT STEPS:
echo.
echo 1. Get Gemini API Key:
echo    - Visit: https://ai.google.dev
echo    - Click "Get API Key" and create a new key
echo    - Copy the API key
echo.
echo 2. Add API Key to backend\.env
echo    - Open: backend\.env
echo    - Find: GEMINI_API_KEY=your_gemini_api_key_here
echo    - Replace with your actual key
echo.
echo 3. Start Backend Server:
echo    - Run: cd backend
echo    - Run: python manage.py runserver
echo    - Server at: http://localhost:8000
echo.
echo 4. Start Frontend Server (new terminal):
echo    - Run: cd frontend
echo    - Run: npm run dev
echo    - Frontend at: http://localhost:5173
echo.
echo 5. Test the Chatbot:
echo    - Open http://localhost:5173 in browser
echo    - Click the chat icon in bottom-right
echo    - Start chatting!
echo.
echo DOCUMENTATION:
echo   - Main Guide: CHATBOT_QUICKSTART.md
echo   - Backend Setup: backend\CHATBOT_SETUP.md
echo.
echo Happy coding! ^_^
echo.
pause
