import logging
from typing import Optional

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class WhisperAdapter:
    def __init__(
        self,
        model_size: str = "large-v3",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model: Optional[WhisperModel] = None

    @property
    def model(self) -> WhisperModel:
        if self._model is None:
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def transcribe(self, audio_path: str, language: str = "zh") -> dict:
        try:
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                beam_size=5,
                vad_filter=True,
            )

            segment_list = []
            full_text_parts = []
            for i, segment in enumerate(segments):
                segment_list.append({
                    "id": i,
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip(),
                })
                full_text_parts.append(segment.text.strip())

            return {
                "success": True,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": round(info.duration, 2),
                "full_text": " ".join(full_text_parts),
                "segments": segment_list,
            }
        except Exception as e:
            logger.exception("Transcription failed")
            return {"success": False, "error": str(e)}
