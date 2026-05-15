@echo off
cd /d %~dp0

echo ============================================
echo   ATRI Chat - Environment Setup
echo ============================================
echo.

echo [Prerequisites - Install these first:]
echo   1. Python 3.9  https://www.python.org/downloads/
echo   2. Ollama      https://ollama.com/download
echo   3. ffmpeg      https://ffmpeg.org/download.html
echo      (or place ffmpeg.exe + ffprobe.exe in project root)
echo.
echo   After installing Ollama, create the ATRI model:
echo     ollama create ATRI -f ATRI
echo.
echo ============================================
echo.

REM ---- Check Python ----
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.9 not found.
    pause
    exit /b 1
)

REM ---- Create venv ----
if exist venv\ (
    echo [SKIP] venv/ already exists
) else (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
    echo   Done.
)

REM ---- Install deps ----
echo [2/4] Installing Python dependencies...
venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed
    pause
    exit /b 1
)
echo   Done.

REM ---- Download pretrained models ----
echo [3/4] Downloading pretrained TTS models...
venv\Scripts\python download_models.py
if %errorlevel% neq 0 (
    echo [ERROR] Model download failed
    pause
    exit /b 1
)
echo   Done.

REM ---- Place custom weights ----
echo [4/4] Setting up custom weights...
if not exist GPT_weights_v2\ (
    echo   [INFO] GPT_weights_v2/ not found.
    echo   - Place your GPT model weights in GPT_weights_v2/
)
if not exist SoVITS_weights_v2\ (
    echo   [INFO] SoVITS_weights_v2/ not found.
    echo   - Place your SoVITS model weights in SoVITS_weights_v2/
)
if not exist ref\*.wav (
    echo   [INFO] No .wav found in ref/.
    echo   - Place your TTS reference audio in ref/
)
echo   Done.

echo.
echo ============================================
echo   Setup complete! Before running, check:
echo.
echo   1. ref/             - contains your reference audio (.wav)
echo   2. GPT_weights_v2/  - contains your GPT model weights
echo   3. SoVITS_weights_v2/ - contains your SoVITS model weights
echo   4. Make sure Ollama is running
echo   5. ollama create ATRI -f ATRI    (first time only)
echo   6. gui.bat                        (launch the app)
echo ============================================
echo.
pause
