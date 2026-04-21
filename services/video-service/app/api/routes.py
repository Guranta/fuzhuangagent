from fastapi import APIRouter, HTTPException, Request

from app.pipeline.processor import VideoPipeline
from app.schemas.contracts import VideoProcessResponse
from pydantic import BaseModel, HttpUrl


class VideoProcessRequest(BaseModel):
    video_url: HttpUrl


router = APIRouter()


@router.post("/video/process", response_model=VideoProcessResponse)
async def process_video(payload: VideoProcessRequest, request: Request):
    downloader = getattr(request.app.state, "downloader", None)
    whisper = getattr(request.app.state, "whisper", None)
    if downloader is None or whisper is None:
        raise HTTPException(status_code=503, detail="Video processing dependencies are not ready")

    pipeline = VideoPipeline(downloader=downloader, whisper=whisper)
    result = await pipeline.process(str(payload.video_url))
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Video processing failed"))

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
