from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.adapters.whisper_adapter import WhisperAdapter
from app.adapters.ytdlp_adapter import YtDlpAdapter
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.whisper = WhisperAdapter(
        model_size=settings.WHISPER_MODEL,
        device=settings.WHISPER_DEVICE,
        compute_type=settings.WHISPER_COMPUTE_TYPE,
    )
    app.state.downloader = YtDlpAdapter(output_dir=settings.VIDEO_DOWNLOAD_DIR)
    yield
    app.state.whisper = None
    app.state.downloader = None
