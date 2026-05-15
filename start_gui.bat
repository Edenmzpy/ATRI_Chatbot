@echo off
cd /d %~dp0
echo Starting GUI...
venv\Scripts\python.exe gui.py
pause
