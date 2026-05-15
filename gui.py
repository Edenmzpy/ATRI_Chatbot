import os
import sys
import time
import threading
import re
import json
import glob

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import yaml
import requests
import pygame
import live2d.v3 as live2d
from live2d.v3 import StandardParams
from live2d.utils.lipsync import WavHandler
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPalette, QBrush, QPainter, QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QMainWindow, QOpenGLWidget, QSplitter,
)

import genie_tts as genie
from genie_tts.Core.Inference import tts_client as _genie_tts_client


def load_config():
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


config = load_config()
dialog_url = config['dialog_url']
headers = {'Content-Type': 'application/json'}


class Live2DWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        pygame.init()
        pygame.mixer.init()
        live2d.init()
        super().__init__(parent)
        self.RESOURCES_DIRECTORY = os.path.join(os.getcwd(), "Live_2d_models")
        self.model = None
        self.wavHandler = WavHandler()
        self.audioPlayed = False
        self.dx = 0.0
        self.dy = 0.0
        self.scale = 1.0
        self.lipSyncN = 2.5
        self.audioPath = None
        self.background_path = None
        self.background_image = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_audio_playback)
        self.timer.start(100)

    def check_audio_playback(self):
        if self.audioPath and not self.audioPlayed:
            self.start_audio()

    def initializeGL(self):
        live2d.glInit()
        self.model = live2d.LAppModel()
        self.model.LoadModelJson(
            os.path.join(self.RESOURCES_DIRECTORY, config['live2d_model'])
        )
        self.model.SetAutoBlinkEnable(True)
        self.model.SetAutoBreathEnable(True)
        if self.background_path:
            self.background_image = QImage(self.background_path)
        else:
            self.background_image = None

    def resizeGL(self, w, h):
        self.model.Resize(w, h)

    def paintGL(self):
        live2d.clearBuffer(1.0, 1.0, 1.0, 1.0)

        if self.background_image:
            background_scaled = self.background_image.scaled(
                self.width(), self.height()
            )
            painter = QPainter(self)
            painter.begin(self)
            painter.drawImage(0, 0, background_scaled)
            painter.end()

        self.model.Update()
        if self.wavHandler.Update():
            self.model.AddParameterValue(
                StandardParams.ParamMouthOpenY,
                self.wavHandler.GetRms() * self.lipSyncN,
            )

        self.model.SetOffset(self.dx, self.dy)
        self.model.SetScale(self.scale)
        self.model.Draw()
        self.update()

    def start_audio(self):
        if self.audioPath and not self.audioPlayed:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.audioPath)
            pygame.mixer.music.play()
            self.wavHandler.Start(self.audioPath)
            self.audioPlayed = True
            self.update_lipsync()
            # Clean up old TTS temp files
            self._cleanup_old_audio()

    def _cleanup_old_audio(self):
        old = [f for f in glob.glob(os.path.join(os.path.dirname(__file__), "tts_*.wav"))
               if f != self.audioPath]
        for f in old:
            try:
                os.remove(f)
            except OSError:
                pass

    def update_lipsync(self):
        if self.wavHandler.Update():
            self.model.AddParameterValue(
                StandardParams.ParamMouthOpenY,
                self.wavHandler.GetRms() * self.lipSyncN,
            )

    def set_background(self, image_path):
        self.background_path = image_path
        if self.background_image:
            self.background_image = QImage(image_path)
        self.update()


class ChatApp(QWidget):
    # Thread-safe signals for cross-thread GUI updates
    append_text_signal = pyqtSignal(str)        # append text to chat
    append_error_signal = pyqtSignal(str)       # show error message
    tts_ready_signal = pyqtSignal(str)          # audio file ready for playback

    def __init__(self, live2d_widget):
        super().__init__()
        self.live2d_widget = live2d_widget
        self.initUI()
        pygame.mixer.init()
        self._set_live2d_background()
        self._init_tts()

        # Connect signals (main thread)
        self.append_text_signal.connect(self._append_text)
        self.append_error_signal.connect(self._append_error)
        self.tts_ready_signal.connect(self._on_tts_ready)

    def _append_text(self, text):
        self.chat_window.insertPlainText(text)

    def _append_error(self, msg):
        self.chat_window.append(msg)

    def _on_tts_ready(self, audio_path):
        # Runs in main thread — safe to access pygame mixer
        self.live2d_widget.audioPath = audio_path
        self.live2d_widget.audioPlayed = False

    def _init_tts(self):
        """Load TTS character model and set reference audio."""
        try:
            genie.load_character(config['character_name'],
                                 config['onnx_model_dir'],
                                 language='chinese')
            genie.set_reference_audio(
                config['character_name'],
                config['ref_audio_path'],
                config['ref_prompt_text'],
                language='chinese')
            print("TTS model loaded.")
        except Exception as e:
            msg = f"TTS init failed: {e}"
            print(msg)
            self.append_error_signal.emit(f"[TTS] {msg}")

    def initUI(self):
        self.setWindowTitle("None")
        self.setGeometry(500, 500, 800, 600)
        layout = QVBoxLayout()

        self.chat_window = QTextEdit(self)
        self.chat_window.setReadOnly(True)
        layout.addWidget(self.chat_window)

        self.set_chat_background(config['chat_background'])

        self.entry_box = QLineEdit(self)
        self.entry_box.returnPressed.connect(self.ask_question)
        layout.addWidget(self.entry_box)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.ask_question)
        layout.addWidget(self.send_button)

        self.setLayout(layout)
        self.conversation_history = []

    def _set_live2d_background(self):
        bg = config.get('live2d_background')
        if bg:
            self.live2d_widget.set_background(bg)

    def set_chat_background(self, image_path):
        oImage = QImage(image_path)
        sImage = oImage.scaled(self.chat_window.size())
        palette = QPalette()
        palette.setBrush(QPalette.Base, QBrush(sImage))
        palette.setColor(QPalette.Text, Qt.white)
        self.chat_window.setPalette(palette)

    def resizeEvent(self, event):
        self.set_chat_background(config['chat_background'])
        super().resizeEvent(event)

    def ask_question(self):
        prompt = self.entry_box.text()
        if prompt.lower() == 'exit':
            self.close()
            return

        if prompt:
            self.conversation_history.append(prompt)

        context = "\n".join(self.conversation_history[-10:])
        data = {
            "model": config['chat_model'],
            "prompt": context,
        }

        self.entry_box.clear()
        if prompt:
            self.chat_window.append(f"{config['user_name']}:{prompt}\n")
        threading.Thread(
            target=self.send_request, args=(data,), daemon=True
        ).start()

    def send_request(self, data, retries=3):
        import requests.exceptions as req_err

        for attempt in range(retries):
            try:
                with requests.post(
                    dialog_url, headers=headers, json=data, stream=True, timeout=(5, 60)
                ) as response:
                    bot_response = ""
                    self.append_text_signal.emit(f"{config['chat_robot_name']}:")
                    for line in response.iter_lines():
                        if line:
                            response_data = json.loads(line)
                            if 'response' in response_data:
                                bot_response += response_data['response']
                                self.append_text_signal.emit(
                                    response_data['response']
                                )
                            if 'done' in response_data and response_data['done']:
                                self.append_text_signal.emit("\n")
                                break
                    self.conversation_history.append(bot_response)
                    self.text_to_speech(bot_response)
                    return  # success
            except (req_err.ConnectionError, req_err.Timeout) as e:
                msg = f"[API] 连接失败(尝试 {attempt+1}/{retries}): {e}"
                print(msg)
                if attempt < retries - 1:
                    self.append_error_signal.emit(f"[API] 正在重试({attempt+2}/{retries})...")
                    time.sleep(1.5 * (attempt + 1))  # 1.5s, 3s, 4.5s backoff
                else:
                    self.append_error_signal.emit(f"[API] 连接失败: {e}")
            except Exception as e:
                self.append_error_signal.emit(f"[API] 请求异常: {e}")
                print(f"Can't load llm: {e}")
                return  # non-retryable, give up

    def text_to_speech(self, text):
        try:
            cleaned_text = re.sub(r'\(.*?\)', '', text)
            if not cleaned_text.strip():
                print(f"TTS skipped: empty text after cleaning '{text}'")
                return

            # Unique filename per TTS to avoid Windows file-lock conflicts
            audio_path = os.path.join(
                os.path.dirname(__file__),
                f"tts_{int(time.time() * 1000)}.wav"
            )

            print(f"TTS starting for: '{cleaned_text[:80]}...' -> {audio_path}")
            # Clear any stale stop_event from prior interrupted sessions
            _genie_tts_client.stop_event.clear()
            genie.tts(config['character_name'], cleaned_text,
                      play=False, split_sentence=False, save_path=audio_path)
            print("TTS returned successfully")

            if os.path.isfile(audio_path) and os.path.getsize(audio_path) > 0:
                print(f"TTS OK: {os.path.getsize(audio_path)} bytes -> {audio_path}")
                self.tts_ready_signal.emit(audio_path)
            else:
                exists = os.path.exists(audio_path)
                size = os.path.getsize(audio_path) if exists else 0
                print(f"TTS empty: file_exists={exists}, size={size}, text='{cleaned_text[:50]}'")
                self.append_error_signal.emit(f"[TTS] 生成的音频为空 (file={exists}, size={size})")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.append_error_signal.emit(f"[TTS] 生成语音失败: {e}")
            print(f"TTS failed: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config['window_name'])
        self.setGeometry(1200, 600, 800, 800)
        self.setWindowIcon(QIcon(config['icon_image']))

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        splitter = QSplitter(Qt.Horizontal, main_widget)
        self.live2d_widget = Live2DWidget(self)
        self.chat_app = ChatApp(self.live2d_widget)

        splitter.addWidget(self.chat_app)
        splitter.addWidget(self.live2d_widget)
        splitter.setSizes([600, 600])
        layout = QVBoxLayout(main_widget)
        layout.addWidget(splitter)

        self._set_black_background()

    def _set_black_background(self):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
