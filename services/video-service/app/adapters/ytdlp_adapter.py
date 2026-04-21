import os
import logging
from typing import Optional

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

logger = logging.getLogger(__name__)


class YtDlpAdapter:
    SUPPORTED_PLATFORMS = {"douyin.com", "www.douyin.com", "xiaohongshu.com", "www.xiaohongshu.com", "kuaishou.com", "www.kuaishou.com", "v.kuaishou.com", "bilibili.com", "www.bilibili.com"}

    def __init__(self, output_dir: str = "/tmp/fashion-agent/videos"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def download(self, url: str, cookie_file: Optional[str] = None) -> dict:
        output_path = os.path.join(self.output_dir, "%(title).50s.%(ext)s")
        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": output_path,
            "retries": 5,
            "fragment_retries": 5,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            },
            "quiet": True,
            "no_warnings": True,
        }

        if cookie_file:
            ydl_opts["cookiefile"] = cookie_file

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info is None:
                    return {"success": False, "error": "Video unavailable or removed"}
                video_path = ydl.prepare_filename(info)
                return {
                    "success": True,
                    "video_path": video_path,
                    "metadata": {
                        "title": info.get("title", ""),
                        "duration": info.get("duration", 0),
                        "uploader": info.get("uploader", ""),
                        "description": info.get("description", ""),
                        "thumbnail": info.get("thumbnail", ""),
                    },
                }
        except DownloadError as e:
            error_msg = str(e).lower()
            if "unavailable" in error_msg:
                return {"success": False, "error": "Video unavailable or removed"}
            elif "age restriction" in error_msg:
                return {"success": False, "error": "Age-restricted content"}
            elif "sign in" in error_msg or "login" in error_msg:
                return {"success": False, "error": "Login required for this video"}
            return {"success": False, "error": f"Download failed: {e}"}
        except ExtractorError as e:
            return {"success": False, "error": f"Extraction failed: {e}"}
        except Exception as e:
            logger.exception("Unexpected download error")
            return {"success": False, "error": f"Unexpected error: {e}"}

    def get_info(self, url: str) -> dict:
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    return {"success": False, "error": "Cannot extract video info"}
                return {"success": True, "metadata": {
                    "title": info.get("title", ""),
                    "duration": info.get("duration", 0),
                    "uploader": info.get("uploader", ""),
                    "description": info.get("description", ""),
                }}
        except Exception as e:
            return {"success": False, "error": str(e)}
