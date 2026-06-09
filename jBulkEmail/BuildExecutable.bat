@echo off
SETLOCAL EnableDelayedExpansion
mode con: cols=75 lines=30
color 0B
@echo =======================================
echo      jBulkEmailSender Build Hub v6.1
echo =======================================
echo.
echo [INFO] Initiating construction of standalone Mission Executable...
echo.

cd /d "%~dp0"
REM --- USER REQUESTED: Force Create the Package Folder Immediately ---
mkdir PACKAGE_READY_TO_ZIP 2>nul
echo [SUCCESS] Package folder created/verified.
echo.

REM 1. Verify Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your Windows PATH.
    echo.
    echo PLEASE: 
    echo 1. Install Python from python.org
    echo 2. Check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

REM 2. Install dependencies first
echo [INFO] Installing Tactical Systems...
python -m pip install -r requirements.txt --quiet
python -m pip install pyinstaller --quiet

REM 3. Run the Build Script
echo [INFO] Commencing PyInstaller mission...
python build_dist.py

if errorlevel 1 (
    echo.
    echo [CRITICAL ERROR] The builder failed to construct the package.
    echo Check the messages above for the reason.
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] MISSION COMPLETE.
echo [ACTION] Please navigate to the 'PACKAGE_READY_TO_ZIP' folder.
echo [ACTION] Zip the 'jBulkEmailSender' folder and share it!
echo.
pause
