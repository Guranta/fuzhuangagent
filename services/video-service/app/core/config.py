from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "Fashion Agent - Video Processing Service"
    APP_VERSION: str = "0.1.0"

    WHISPER_MODEL: str = "large-v3"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"

    VIDEO_DOWNLOAD_DIR: str = "/tmp/fashion-agent/videos"
    VIDEO_PROCESS_TIMEOUT: int = 300

    TRANSNETV2_DEVICE: str = "auto"
    TRANSNETV2_THRESHOLD: float = 0.5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
