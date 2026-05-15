@echo off
cd /d %~dp0
echo Starting ATRI Chatbot...
start "" /min cmd /c "venv\Scripts\python.exe gui.py"
exit
