"""Genie-TTS API server wrapper.

Sets up the environment and starts the Genie-TTS FastAPI server.
Provides POST endpoints:
  /load_character       - Load an ONNX character model
  /set_reference_audio  - Set reference audio for voice cloning
  /tts                  - Generate speech (streaming WAV)
  /stop                 - Stop current TTS
"""
import os
import sys

# Point to our HuBERT ONNX model
hubert_path = os.path.join(os.path.dirname(__file__), "genie_data",
                           "chinese-hubert-base", "chinese-hubert-base.onnx")
if os.path.isfile(hubert_path):
    os.environ["HUBERT_MODEL_PATH"] = hubert_path

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import genie_tts as genie

if __name__ == "__main__":
    genie.start_server(host="0.0.0.0", port=9880, workers=1)
