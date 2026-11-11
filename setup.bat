@echo off
cd /d %~dp0

echo ============================================
echo   ATRI Chat - Environment Setup
echo ============================================
echo.

echo [Prerequisites - Install these first:]
echo   1. Python 3.9  https://www.python.org/downloads/
echo   2. Ollama      https://ollama.com/download
echo.
echo   After installing Ollama, create the ATRI model:
echo     ollama create ATRI -f ollama/ATRI.Modelfile
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
    echo [1/3] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
    echo   Done.
)

REM ---- Install deps ----
echo [2/3] Installing Python dependencies...
venv\Scripts\pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed
    pause
    exit /b 1
)
echo   Done.

REM ---- Prepare local config and check models ----
echo [3/3] Preparing local configuration...
if not exist config.yaml (
    copy /Y config.example.yaml config.yaml >nul
    echo   Created config.yaml from config.example.yaml
) else (
    echo   [SKIP] config.yaml already exists
)

if not exist onnx_model\your-character\ (
    echo   [INFO] ONNX model not found. To convert your GPT-SoVITS models:
    echo     venv\Scripts\python -c "import genie_tts as genie; genie.convert_to_onnx('GPT_weights_v2/your_model.ckpt', 'SoVITS_weights_v2/your_model.pth', 'onnx_model/your-character')"
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
echo   1. config.yaml      - matches your model and audio paths
echo   2. ref/             - contains your reference audio (.wav)
echo   3. onnx_model/      - contains converted ONNX model
echo   4. GenieData/       - contains TTS model (HuBERT/G2P/RoBERTa)
echo   5. Make sure Ollama is running
echo   6. ollama create ATRI -f ollama/ATRI.Modelfile   (first time only)
echo   7. gui.bat                        (launch the app)
echo ============================================
echo.
pause
