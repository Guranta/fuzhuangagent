import warnings
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "Fashion Agent - Video Processing Service"
    APP_VERSION: str = "0.1.0"
    APP_ENV: Literal["production", "development"] = "production"
    LOG_LEVEL: str = "INFO"
    VIDEO_SERVICE_PORT: int = Field(default=8000, ge=1, le=65535)
    VIDEO_SERVICE_WORKERS: int = Field(default=1, ge=1)

    WHISPER_MODEL: str = "base"
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"

    VIDEO_DOWNLOAD_DIR: str = "/tmp/fashion-agent/videos"
    VIDEO_PROCESS_TIMEOUT: int = Field(default=300, gt=0)

    TRANSNETV2_DEVICE: str = "auto"
    TRANSNETV2_THRESHOLD: float = Field(default=0.5, ge=0.0, le=1.0)

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper()
        return value

    @model_validator(mode="after")
    def warn_on_heavy_whisper_model(self) -> "Settings":
        if self.APP_ENV == "production" and self.WHISPER_MODEL == "large-v3":
            warnings.warn(
                "WHISPER_MODEL=large-v3 may be too heavy for typical VPS production deployments.",
                stacklevel=2,
            )
        return self

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
