@echo off
SETLOCAL EnableDelayedExpansion
REM Set Tactical Terminal Dimensions
mode con: cols=65 lines=25
color 0A
REM jBulkEmailSender Launcher (Tactical Operations)
REM Launches the Python application and handles dependencies

echo.
echo           _________________________
echo          /   ___________________   \
echo         /   /                   \   \
echo        /   /      NCC-1031       \   \
echo       ^|   ^|        _______        ^|   ^|
echo       ^|   ^|       /       \       ^|   ^|
echo        \   \_____/         \_____/   /
echo         \___________________________/
echo               ^| ^|         ^| ^|
echo               ^| ^|_________^| ^|
echo               ^|_____________^|
echo.
echo =======================================
echo         jBulkEmailSender
echo   jBES DISCOVERY COMMAND CONSOLE
echo =======================================
echo.

cd /d "%~dp0"

REM 1. Tactical Engine Selection (Local vs System)
SET "PYTHON_EXE=python"
IF EXIST "python_engine\python.exe" (
    SET "PYTHON_EXE=%~dp0python_engine\python.exe"
    echo [INFO] Using Integrated Tactical Engine...
) ELSE (
    python --version >nul 2>&1
    IF ERRORLEVEL 1 (
        echo [ERROR] No Mission Engine Found!
        echo.
        echo PRO-TIP: Create a 'python_engine' folder with an embeddable 
        echo Python distribution to make this app 100%% portable.
        echo.
        pause
        exit /b 1
    )
    echo [INFO] Using System Python Engine...
)

REM 2. Check and install dependencies automatically
echo [INFO] Verifying Tactical Systems (Dependencies)...
"%PYTHON_EXE%" -m pip install -r requirements.txt --quiet
IF ERRORLEVEL 1 (
    echo [WARNING] Automatic dependency installation failed or pip missing in local engine.
    echo [INFO] Attempting fallback execution...
)

echo [SUCCESS] Tactical Systems Ready.
echo.
echo [INFO] Initiating Bulk Transmission Console...
echo.

REM 3. Run the application in background and close terminal
REM Use pythonw if using local engine for silent launch
IF EXIST "python_engine\pythonw.exe" (
    start /b "" "%~dp0python_engine\pythonw.exe" bulk_email_sender.py
) ELSE (
    start /b "" "%PYTHON_EXE%w" bulk_email_sender.py
)

ENDLOCAL
exit
