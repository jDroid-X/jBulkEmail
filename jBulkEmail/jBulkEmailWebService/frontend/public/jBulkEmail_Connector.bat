@echo off
title jBulkEmail Local Engine Connector
color 0B
echo ==============================================================
echo 🚀 jBulkEmail SaaS - Local Engine Installation & Connection
echo ==============================================================
echo.

set "TARGET_DIR=%USERPROFILE%\Desktop\BulkEmail\Engine"

if not exist "%TARGET_DIR%" (
    echo [1/4] Constructing Local Engine Directory...
    mkdir "%TARGET_DIR%"
)

cd /d "%TARGET_DIR%"

echo [2/4] Downloading latest Engine Core from Cloud...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/jDroid-X/jBulkEmail/archive/refs/heads/main.zip' -OutFile 'engine.zip'"

echo [3/4] Extracting Engine Files...
powershell -Command "Expand-Archive -Path 'engine.zip' -DestinationPath '.' -Force"
del engine.zip

cd "jBulkEmail-main\jBulkEmailWebService"

echo [4/4] Verifying Python Dependencies...
pip install -r backend/requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [!] Warning: Missing Python or failed to install requirements.
    echo Please ensure Python 3.9+ is installed and added to PATH.
    pause
    exit /b
)

echo.
echo ==============================================================
echo ✅ Engine Installed Successfully! 
echo ⚡ Starting Local API Server on Port 8000...
echo Do not close this window while using the jBulkEmail Website!
echo ==============================================================

cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
