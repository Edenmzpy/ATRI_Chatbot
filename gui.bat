@echo off
cd /d %~dp0
echo Starting TTS API server...
start "" /min cmd /c "venv\Scripts\python.exe api_v2.py"

echo Waiting for API server to start...
timeout /t 3 /nobreak >nul

echo Starting GUI...
start "" /min cmd /c "venv\Scripts\python.exe gui.py"
exit
