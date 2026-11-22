@echo off
title Budget Tracker
cd /d "%~dp0"

rem ---- 1+2. First time only: check Python, create a private Python space, install tools ----
if exist ".venv\setup_done.txt" goto :start
python --version >nul 2>nul
if errorlevel 1 (
    echo.
    echo  Python is not installed yet ^(or was installed without "Add to PATH"^).
    echo  Please follow Step 1 in README.md, restart your computer,
    echo  then double-click run.bat again.
    echo.
    pause
    exit /b 1
)
if not exist ".venv\setup_done.txt" (
    echo.
    echo  First-time setup: installing what the app needs.
    echo  This takes 1-3 minutes and only happens once...
    echo.
    if not exist ".venv\Scripts\python.exe" python -m venv .venv
    if errorlevel 1 goto :failed
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :failed
    echo done> ".venv\setup_done.txt"
)

:start
rem ---- 3. Start the app and open the browser ----
echo.
echo  Starting Budget Tracker... your browser will open in a few seconds.
echo  If it doesn't, open this address yourself:  http://localhost:8501
echo.
echo  KEEP THIS WINDOW OPEN while you use the app. Close it to stop the app.
echo.
start "" /b powershell -NoProfile -Command "Start-Sleep -Seconds 4; Start-Process 'http://localhost:8501'"
".venv\Scripts\python.exe" -m streamlit run app.py
pause
exit /b 0

:failed
echo.
echo  Something went wrong during setup. Check your internet connection
echo  and try again. If it keeps failing, copy the messages above and ask for help.
echo.
pause
exit /b 1
