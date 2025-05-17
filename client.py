# 客户端伪代码

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # 初始化UI
        self.init_ui()

        # 初始化音频设备
        self.audio_recorder = AudioRecorder()
        self.audio_player = AudioPlayer()

        # 初始化网络客户端
        self.api_client = APIClient(server_url)

        # 用户ID (首次启动时生成)
        self.user_id = generate_user_id()

        # 首次连接服务器
        self.initialize_session()

    def init_ui(self):
        """
        初始化用户界面
        """
        # 创建录音按钮
        self.record_button = QPushButton("按住说话")
        self.record_button.pressed.connect(self.start_recording)
        self.record_button.released.connect(self.stop_recording)

        # 创建状态标签
        self.status_label = QLabel("准备就绪")

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.record_button)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def initialize_session(self):
        """
        初始化与服务器的会话
        """
        # 显示连接状态
        self.status_label.setText("正在连接服务器...")

        # 请求服务器初始化会话
        welcome_audio = self.api_client.initialize_session(self.user_id)

        # 播放欢迎音频
        self.play_audio(welcome_audio)

        # 更新状态
        self.status_label.setText("准备就绪")

    def start_recording(self):
        """
        开始录音
        """
        self.status_label.setText("正在聆听...")
        self.audio_recorder.start()

    def stop_recording(self):
        """
        停止录音并发送到服务器
        """
        # 停止录音
        audio_data = self.audio_recorder.stop()
        self.status_label.setText("正在处理...")

        # 发送音频到服务器
        reply_audio = self.api_client.process_audio(self.user_id, audio_data)

        # 播放回复
        self.play_audio(reply_audio)

        # 更新状态
        self.status_label.setText("准备就绪")

    def play_audio(self, audio_data):
        """
        播放音频
        """
        self.audio_player.play(audio_data)


class APIClient:

    def __init__(self, server_url):
        self.server_url = server_url

    def initialize_session(self, user_id):
        """
        初始化会话
        """
        response = post(server_url + "/api/initialize_session", json={"user_id": user_id})
        return response.audio_data

    def process_audio(self, user_id, audio_data):
        """
        处理用户音频
        """
        response = post(server_url + "/api/process_audio",
                        json={"user_id": user_id},
                        files={"audio": audio_data})
        return response.audio_data