import logging

logger = logging.getLogger(__name__)


class TransNetV2Adapter:
    def __init__(self, device: str = "auto", threshold: float = 0.5):
        self.device = device
        self.threshold = threshold
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                from transnetv2_pytorch import TransNetV2
                logger.info(f"Loading TransNetV2 on {self.device}")
                self._model = TransNetV2(device=self.device)
            except ImportError:
                logger.warning("transnetv2-pytorch not installed, scene detection disabled")
                return None
        return self._model

    def detect_scenes(self, video_path: str) -> dict:
        if self.model is None:
            return {"success": False, "error": "TransNetV2 not available", "scenes": []}

        try:
            scenes = self.model.detect_scenes(video_path, threshold=self.threshold)
            scene_list = []
            for scene in scenes:
                scene_list.append({
                    "shot_id": scene.get("shot_id", len(scene_list)),
                    "start_time": round(scene.get("start_time", 0), 2),
                    "end_time": round(scene.get("end_time", 0), 2),
                })

            return {
                "success": True,
                "scene_count": len(scene_list),
                "scenes": scene_list,
            }
        except Exception as e:
            logger.exception("Scene detection failed")
            return {"success": False, "error": str(e), "scenes": []}
