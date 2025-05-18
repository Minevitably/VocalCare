import requests
from loguru import logger
from client import APIClient



if __name__ == "__main__":
    # 测试API客户端
    logger.add("client_test.log", rotation="1 MB", level="DEBUG")

    try:
        client = APIClient("http://localhost:5000")

        # 测试初始化会话
        test_user = "test_user_001"
        logger.info(f"Initializing session for user {test_user}")
        welcome_audio = client.initialize_session(test_user)

        with open('client_welcome.wav', 'wb') as f:
            f.write(welcome_audio)
            logger.info("Saved welcome audio to client_welcome.wav")

        # 测试处理音频
        logger.info("Processing test audio")
        with open('test_audio.pcm', 'rb') as f:
            test_audio = f.read()

        reply_audio = client.process_audio(test_user, test_audio)

        with open('client_reply.wav', 'wb') as f:
            f.write(reply_audio)
            logger.info("Saved reply audio to client_reply.wav")

    except Exception as e:
        logger.error(f"Client test failed: {e}")