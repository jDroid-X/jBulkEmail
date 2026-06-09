@echo off
title jBulkEmailWebService Launcher

echo ===================================================
echo 🚀 Bootstrapping jBulkEmailWebService SaaS Platform
echo ===================================================

echo [1/4] Installing Python Backend dependencies...
pip install -r backend/requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Failed to install some requirements. Ensuring core libraries are manually present...
    pip install fastapi uvicorn sqlalchemy pydantic pyjwt passlib bcrypt python-multipart websockets requests
)

echo [2/4] Initializing Database Schema...
python -c "import sys; sys.path.append('backend'); from database.db_setup import init_db; init_db()"

echo [3/4] Installing React Frontend dependencies...
cd frontend
call npm.cmd install
cd ..

echo [4/4] Starting servers...
echo Starting FastAPI Server on http://localhost:8000
start cmd /k "title FastAPI Backend && cd backend && python main.py"

echo Starting React Vite Server on http://localhost:5173
start cmd /k "title React Frontend && cd frontend && npm.cmd run dev"

echo ===================================================
echo ✅ Startup sequence triggered! 
echo Backend API: http://localhost:8000/docs
echo Frontend UI: http://localhost:5173/
echo ===================================================
pause
