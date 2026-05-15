import yaml
import sys
import requests
import json
import threading
import re
import pygame
import io
import os
from pydub import AudioSegment
import live2d.v3 as live2d
from live2d.v3 import StandardParams
from live2d.utils.lipsync import WavHandler
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPalette, QBrush, QPainter, QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QMainWindow, QOpenGLWidget, QSplitter,
)


def load_config():
    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


config = load_config()
dialog_url = config['dialog_url']
tts_url = config['tts_url']
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
            pygame.mixer.music.load(self.audioPath)
            pygame.mixer.music.play()
            self.wavHandler.Start(self.audioPath)
            self.audioPlayed = True
            self.update_lipsync()

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
    def __init__(self, live2d_widget):
        super().__init__()
        self.live2d_widget = live2d_widget
        self.initUI()
        pygame.mixer.init()
        self._set_live2d_background()

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

    def send_request(self, data):
        try:
            with requests.post(
                dialog_url, headers=headers, json=data, stream=True
            ) as response:
                bot_response = ""
                self.chat_window.append(f"{config['chat_robot_name']}:")
                for line in response.iter_lines():
                    if line:
                        response_data = json.loads(line)
                        if 'response' in response_data:
                            bot_response += response_data['response']
                            self.chat_window.insertPlainText(
                                response_data['response']
                            )
                        if 'done' in response_data and response_data['done']:
                            self.chat_window.append("")
                            break
                self.conversation_history.append(bot_response)
                self.text_to_speech(bot_response)
        except Exception as e:
            print(f"Can't load llm: {e}")

    def text_to_speech(self, text):
        try:
            cleaned_text = re.sub(r'\(.*?\)', '', text)
            data = {
                "text": cleaned_text,
                "text_lang": config['text_lang'],
                "ref_audio_path": config['ref_audio_path'],
                "prompt_lang": config['prompt_lang'],
                "prompt_text": config['ref_prompt_text'],
                "top_k": 5,
                "top_p": 1,
                "temperature": 1,
                "text_split_method": "cut5",
                "batch_size": 1,
                "batch_threshold": 0.75,
                "speed_factor": 1.0,
                "media_type": "wav",
                "streaming_mode": False,
            }

            response = requests.post(tts_url, headers=headers, json=data)
            if response.status_code == 200:
                audio_bytes = io.BytesIO(response.content)
                audio_segment = AudioSegment.from_wav(audio_bytes)

                pygame.mixer.quit()
                pygame.mixer.init()

                audio_path = "tts_output.wav"
                audio_segment.export(
                    audio_path, format="wav", parameters=["-ac", "1"]
                )
                self.live2d_widget.audioPath = audio_path
                self.live2d_widget.audioPlayed = False
                self.live2d_widget.start_audio()
            else:
                print(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Fail to play: {e}")


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

        self.live2d_widget.start_audio()
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
