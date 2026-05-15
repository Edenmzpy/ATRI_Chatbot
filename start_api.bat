@echo off
cd /d %~dp0
echo Starting TTS API server...
venv\Scripts\python.exe api_v2.py
pause
