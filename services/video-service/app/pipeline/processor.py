import asyncio
import logging
import os
import subprocess

from app.adapters.transnetv2_adapter import TransNetV2Adapter
from app.adapters.whisper_adapter import WhisperAdapter
from app.adapters.ytdlp_adapter import YtDlpAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)


class VideoPipeline:
    def __init__(
        self,
        downloader: YtDlpAdapter,
        whisper: WhisperAdapter,
    ):
        self.downloader = downloader
        self.whisper = whisper
        self.scene_detector = TransNetV2Adapter(
            device=settings.TRANSNETV2_DEVICE,
            threshold=settings.TRANSNETV2_THRESHOLD,
        )

    async def process(self, video_url: str) -> dict:
        loop = asyncio.get_event_loop()

        download_result = await loop.run_in_executor(
            None, self.downloader.download, video_url
        )
        if not download_result.get("success"):
            return {"success": False, "error": download_result.get("error", "Download failed")}

        video_path = download_result["video_path"]
        metadata = download_result.get("metadata", {})

        try:
            audio_path = await loop.run_in_executor(
                None, self._extract_audio, video_path
            )

            transcript_result = await loop.run_in_executor(
                None, self.whisper.transcribe, audio_path
            )

            scene_result = await loop.run_in_executor(
                None, self.scene_detector.detect_scenes, video_path
            )

            keyframes = await loop.run_in_executor(
                None, self._extract_keyframes, video_path
            )

            return {
                "success": True,
                "video_url": video_url,
                "duration_seconds": metadata.get("duration", 0),
                "title": metadata.get("title", ""),
                "transcript": transcript_result.get("full_text", ""),
                "segments": transcript_result.get("segments", []),
                "scenes": scene_result.get("scenes", []),
                "keyframes": keyframes,
            }
        except Exception as e:
            logger.exception("Pipeline processing failed")
            return {"success": False, "error": str(e)}
        finally:
            self._cleanup(video_path)

    def _extract_audio(self, video_path: str) -> str:
        audio_path = video_path.rsplit(".", 1)[0] + ".wav"
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", "16000", "-ac", "1",
            "-y", audio_path,
        ]
        subprocess.run(cmd, capture_output=True, check=True, timeout=120)
        return audio_path

    def _extract_keyframes(self, video_path: str, num_frames: int = 5) -> list:
        import cv2

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        keyframes = []
        interval = max(total_frames // (num_frames + 1), 1)
        output_dir = os.path.join(settings.VIDEO_DOWNLOAD_DIR, "keyframes")
        os.makedirs(output_dir, exist_ok=True)

        for i in range(1, num_frames + 1):
            frame_idx = interval * i
            if frame_idx >= total_frames:
                break
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                timestamp = round(frame_idx / fps, 2)
                filename = f"kf_{os.path.basename(video_path)}_{i}.jpg"
                filepath = os.path.join(output_dir, filename)
                cv2.imwrite(filepath, frame)
                keyframes.append({
                    "timestamp": timestamp,
                    "frame_index": frame_idx,
                    "image_path": filepath,
                })

        cap.release()
        return keyframes

    def _cleanup(self, video_path: str):
        for ext in ["", ".wav"]:
            path = video_path.rsplit(".", 1)[0] + ext if ext else video_path
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass
