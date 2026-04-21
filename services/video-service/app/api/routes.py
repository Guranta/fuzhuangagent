import asyncio
import logging

from fastapi import APIRouter, HTTPException, Request

from app.pipeline.processor import VideoPipeline
from app.core.config import settings
from app.schemas.contracts import VideoProcessResponse
from pydantic import BaseModel, HttpUrl


class VideoProcessRequest(BaseModel):
    video_url: HttpUrl


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/video/process", response_model=VideoProcessResponse)
async def process_video(payload: VideoProcessRequest, request: Request):
    logger.info(
        "Received video processing request url=%s client=%s",
        payload.video_url,
        request.client.host if request.client else "unknown",
    )

    downloader = getattr(request.app.state, "downloader", None)
    whisper = getattr(request.app.state, "whisper", None)
    if downloader is None or whisper is None:
        logger.warning("Video processing dependencies are not ready")
        raise HTTPException(status_code=503, detail="Video processing dependencies are not ready")

    pipeline = VideoPipeline(downloader=downloader, whisper=whisper)
    try:
        result = await asyncio.wait_for(
            pipeline.process(str(payload.video_url)),
            timeout=settings.VIDEO_PROCESS_TIMEOUT,
        )
    except TimeoutError as exc:
        logger.warning(
            "Video processing timed out url=%s timeout=%ss",
            payload.video_url,
            settings.VIDEO_PROCESS_TIMEOUT,
        )
        raise HTTPException(status_code=504, detail="Video processing timed out") from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected video processing failure url=%s", payload.video_url)
        raise HTTPException(status_code=500, detail="Internal video processing error") from exc

    if not result.get("success"):
        logger.warning(
            "Video processing failed url=%s error=%s",
            payload.video_url,
            result.get("error", "Video processing failed"),
        )
        raise HTTPException(status_code=400, detail=result.get("error", "Video processing failed"))

    logger.info("Video processing completed url=%s", payload.video_url)

    return VideoProcessResponse(
        video_url=result["video_url"],
        duration_seconds=result.get("duration_seconds", 0),
        transcript=result.get("transcript", ""),
        segments=result.get("segments", []),
        scenes=[
            {
                "start_time": scene.get("start_time", 0),
                "end_time": scene.get("end_time", 0),
                "scene_index": scene.get("shot_id", index),
            }
            for index, scene in enumerate(result.get("scenes", []))
        ],
        keyframes=result.get("keyframes", []),
        status="success",
    )
