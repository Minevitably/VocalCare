import time
import uuid

from PySide6.QtWidgets import (QMainWindow, QPushButton, QLabel,
                               QVBoxLayout, QWidget, QApplication)
from PySide6.QtCore import QBuffer, QIODevice, Qt
import requests
from loguru import logger

from PySide6.QtMultimedia import QAudioSource, QMediaDevices, QAudioFormat
from PySide6.QtCore import QBuffer, QIODevice

from PySide6.QtCore import QUrl, QBuffer


from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaPlayer
from PySide6.QtCore import QUrl


class AudioRecorder:
    def __init__(self):
        self.audio_input = None
        self.buffer = None
        self.init_audio_input()

    def init_audio_input(self):
        """初始化音频输入"""
        # 设置音频格式：16kHz采样率，单声道，16位PCM
        self.format = QAudioFormat()
        self.format.setSampleRate(16000)
        self.format.setChannelCount(1)
        self.format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        # 获取音频输入设备
        input_devices = QMediaDevices.audioInputs()
        if not input_devices:
            raise RuntimeError("未找到音频输入设备")

        self.audio_input = QAudioSource(input_devices[0], self.format)

    def start(self):
        """开始录音"""
        # 重新初始化缓冲区，确保完全清空
        self.buffer = QBuffer()
        self.buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        self.audio_input.start(self.buffer)

    def stop(self) -> bytes:
        """停止录音并返回PCM数据"""
        self.audio_input.stop()
        data = self.buffer.data()
        self.buffer.close()
        return bytes(data)



class AudioPlayer:
    def __init__(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

    def play(self, audio_data: bytes):
        """播放 MP3 音频数据"""
        try:
            # 确保播放器状态已重置
            if self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
                self.player.stop()

            # 写入临时文件并播放
            now = time.time()
            with open(f"temp{now}.mp3", "wb") as f:
                f.write(audio_data)

            self.player.setSource(QUrl.fromLocalFile(f"temp{now}.mp3"))
            self.player.play()

        except Exception as e:
            print(f"播放音频时出错: {e}")




class APIClient:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        logger.info(f"API客户端初始化，服务器地址: {self.server_url}")

    def initialize_session(self, user_id: str) -> bytes:
        """初始化会话"""
        try:
            response = requests.post(
                f"{self.server_url}/api/initialize_session",
                json={"user_id": user_id},
                timeout=10
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"初始化会话失败: {str(e)}")
            raise

    def process_audio(self, user_id: str, audio_data: bytes) -> bytes:
        """处理音频"""
        try:
            files = {'audio': ('audio.pcm', audio_data, 'audio/pcm')}
            data = {'user_id': user_id}

            response = requests.post(
                f"{self.server_url}/api/process_audio",
                files=files,
                data=data,
                timeout=15
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"处理音频失败: {str(e)}")
            raise


class MainWindow(QMainWindow):
    def __init__(self, server_url: str):
        super().__init__()
        self.server_url = server_url
        self.is_recording = False  # 是否正在录音
        self.setup_ui()
        self.setup_audio()
        self.setup_network()
        self.initialize_session()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("桑榆伴语")
        self.resize(400, 300)

        # 录音按钮
        self.record_button = QPushButton("开始录音")
        self.record_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                min-height: 80px;
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
            }
            QPushButton:checked {
                background-color: #f44336;
            }
        """)
        self.record_button.setCheckable(True)  # 设置为可切换的按钮
        self.record_button.clicked.connect(self.toggle_recording)

        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px;")
        self.status_label.setWordWrap(True)
        self.status_label.setMaximumWidth(350)

        # 布局
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.record_button)
        layout.addSpacing(20)
        layout.addWidget(self.status_label)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def toggle_recording(self):
        """开始或停止录音"""
        if not self.is_recording:
            # 开始录音
            self.audio_recorder.start()
            self.status_label.setText("正在聆听...")
            self.record_button.setText("停止录音")
            self.status_label.setStyleSheet("color: blue; font-size: 18px;")
            self.is_recording = True
        else:
            # 停止录音并处理
            self.status_label.setText("正在处理...")
            self.status_label.setStyleSheet("color: purple; font-size: 18px;")
            QApplication.processEvents()  # 强制更新UI

            try:
                audio_data = self.audio_recorder.stop()
                reply_audio = self.api_client.process_audio(self.user_id, audio_data)
                self.play_audio(reply_audio)
                self.status_label.setText("准备就绪")
                self.status_label.setStyleSheet("color: black; font-size: 18px;")
            except Exception as e:
                self.show_error(f"处理音频失败: {str(e)}")

            # 录音结束
            self.record_button.setText("开始录音")
            self.is_recording = False

    def setup_audio(self):
        """初始化音频设备"""
        try:
            self.audio_recorder = AudioRecorder()
            self.audio_player = AudioPlayer()
        except Exception as e:
            self.show_error(f"音频设备初始化失败: {str(e)}")
            raise

    def setup_network(self):
        """初始化网络连接"""
        try:
            self.user_id = str(uuid.uuid4())
            self.api_client = APIClient(self.server_url)
        except Exception as e:
            self.show_error(f"网络初始化失败: {str(e)}")
            raise

    def show_error(self, message: str):
        """显示错误信息"""
        self.status_label.setText(f"错误: {message}")
        self.status_label.setStyleSheet("color: red; font-size: 18px;")
        self.status_label.setWordWrap(True)
        self.status_label.setMaximumWidth(350)  # 设置最大宽度

    def initialize_session(self):
        """初始化与服务器的会话"""
        self.status_label.setText("正在连接服务器...")
        QApplication.processEvents()  # 强制更新UI

        try:
            welcome_audio = self.api_client.initialize_session(self.user_id)
            self.play_audio(welcome_audio)
            self.status_label.setText("准备就绪")
            self.status_label.setStyleSheet("color: black; font-size: 18px;")
        except Exception as e:
            self.show_error(f"连接服务器失败: {str(e)}")

    def start_recording(self):
        """开始录音"""
        self.status_label.setText("正在聆听...")
        self.status_label.setStyleSheet("color: blue; font-size: 18px;")
        QApplication.processEvents()  # 强制更新UI
        self.audio_recorder.start()

    def stop_recording(self):
        """停止录音并处理"""
        self.status_label.setText("正在处理...")
        self.status_label.setStyleSheet("color: purple; font-size: 18px;")
        QApplication.processEvents()  # 强制更新UI

        try:
            audio_data = self.audio_recorder.stop()
            reply_audio = self.api_client.process_audio(self.user_id, audio_data)
            self.play_audio(reply_audio)
            self.status_label.setText("准备就绪")
            self.status_label.setStyleSheet("color: black; font-size: 18px;")
        except Exception as e:
            self.show_error(f"处理音频失败: {str(e)}")

    def play_audio(self, audio_data: bytes):
        """播放音频"""
        try:
            self.audio_player.play(audio_data)
        except Exception as e:
            self.show_error(f"播放音频失败: {str(e)}")


if __name__ == "__main__":
    import sys

    # 配置日志
    logger.add("client.log", rotation="1 MB", level="DEBUG")

    # 创建应用
    app = QApplication(sys.argv)

    # 设置服务器地址
    SERVER_URL = "http://localhost:5000"  # 根据实际情况修改

    try:
        window = MainWindow(SERVER_URL)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"应用程序启动失败: {str(e)}")
        sys.exit(1)