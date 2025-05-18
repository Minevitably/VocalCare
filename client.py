import requests
from loguru import logger
from typing import Optional


class APIClient:
    def __init__(self, server_url: str):
        """
        初始化API客户端

        :param server_url: 服务器基础URL (如 "http://localhost:5000")
        """
        self.server_url = server_url.rstrip('/')
        logger.info(f"API client initialized for {self.server_url}")

    def initialize_session(self, user_id: str) -> bytes:
        """
        初始化会话

        :param user_id: 用户唯一ID
        :return: 欢迎音频的二进制数据
        """
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
        """
        处理音频消息

        :param user_id: 用户唯一ID
        :param audio_data: PCM音频二进制数据
        :return: 回复音频的二进制数据
        """
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