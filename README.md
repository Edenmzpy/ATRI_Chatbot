<div align="center">

<img src="docs/assets/hero.webp" alt="ATRI Chatbot" width="100%" />

# ATRI Chatbot

**A Live2D voice companion that runs entirely on your PC.**

**English** · [简体中文](README.zh-CN.md)

![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=flat-square&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local_LLM-111111?style=flat-square&logo=ollama&logoColor=white)
![Live2D](https://img.shields.io/badge/Live2D-avatar-00A4EF?style=flat-square)
![Genie-TTS](https://img.shields.io/badge/Genie--TTS-offline_voice-7B61FF?style=flat-square)
![Windows](https://img.shields.io/badge/Windows-0078D4?style=flat-square&logo=windows&logoColor=white)

</div>

<img src="docs/assets/screenshot.webp" alt="ATRI Chatbot window: chat panel and Live2D avatar" width="100%" />

<img src="docs/assets/how-it-works.webp" alt="Pipeline: you → Ollama → Genie-TTS → playback → Live2D lip sync" width="100%" />

## Quick start

**Needs:** Windows 10/11 · Python 3.9 · [Ollama](https://ollama.com/) · a Genie-TTS (GPT-SoVITS) voice model + a short reference `.wav`

```powershell
git clone https://github.com/Edenmzpy/ATRI_Chatbot.git
cd ATRI_Chatbot
./setup.bat                                    # venv + dependencies + config.yaml

ollama pull openllm/causallm
ollama create ATRI -f ollama/ATRI.Modelfile    # the character persona

./gui.bat                                      # launch
```

Before launching: put the converted voice model in `onnx_model/`, the reference clip in `ref/`, and point `config.yaml` at them.

<details>
<summary>Convert GPT-SoVITS weights to ONNX</summary>

```powershell
venv\Scripts\python -c "import genie_tts as genie; genie.convert_to_onnx('GPT_weights_v2/your_model.ckpt', 'SoVITS_weights_v2/your_model.pth', 'onnx_model/your-character')"
```
</details>

<details>
<summary>Configuration keys</summary>

| Key | Purpose |
| --- | --- |
| `chat_model` | Ollama model name — must match `ollama create` |
| `dialog_url` | Ollama generate endpoint |
| `live2d_model` | Path under `assets/live2d/` |
| `character_name` · `onnx_model_dir` | Genie-TTS speaker and model folder |
| `ref_audio_path` · `ref_prompt_text` | Reference clip and its exact transcript |

Full template: [`config.example.yaml`](config.example.yaml)
</details>

## Project layout

```text
gui.py                  UI, Ollama client, TTS and lip sync
ollama/ATRI.Modelfile   character persona
assets/                 Live2D model, backgrounds, icons
config.example.yaml     settings template
setup.bat · gui.bat     install / launch
```

## Notice

Experimental, Windows-only fan project; model weights and voice clips are not included. ATRI and related character assets belong to their respective rights holders — not licensed for redistribution or commercial use.
