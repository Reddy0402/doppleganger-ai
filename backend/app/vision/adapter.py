import numpy as np
from typing import Dict, Any, List, Optional
from backend.app.vision.detector import FaceDetector, FaceObject
from backend.app.vision.alignment import align_face_5point
from backend.app.vision.quality import assess_face_quality
from backend.app.vision.embeddings import BaseFaceModel, SFaceModel, DeterministicBaselineModel

class FaceModelAdapter:
    def __init__(self, model_name: str = "sface"):
        self.detector = FaceDetector()
        self.active_model_name = model_name
        self.model = self._instantiate_model(model_name)

    def _instantiate_model(self, model_name: str) -> BaseFaceModel:
        if model_name.lower() == "sface":
            sface = SFaceModel()
            if sface.recognizer is not None:
                return sface
            print("[INFO] SFace model not found; falling back to deterministic baseline.")
            return DeterministicBaselineModel()
        elif model_name.lower() == "deterministic":
            return DeterministicBaselineModel()
        else:
            return SFaceModel()

    def set_model(self, model_name: str) -> bool:
        self.model = self._instantiate_model(model_name)
        self.active_model_name = model_name
        return True

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "name": self.model.name,
            "version": self.model.version,
            "dimension": self.model.dimension,
            "detector": "yunet_2023mar" if self.detector.yunet is not None else "haar_cascade"
        }

    def process_image(
        self,
        image_rgb: np.ndarray,
        selected_face_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end vision processing:
        1. Detect faces
        2. Handle zero, one, multiple faces
        3. Assess quality
        4. Align face
        5. Generate embedding & sub-region embeddings
        """
        faces = self.detector.detect(image_rgb)
        
        if len(faces) == 0:
            return {
                "status": "NO_FACE_DETECTED",
                "message": "No face was detected in the uploaded image. Please provide a clear, front-facing portrait with adequate lighting.",
                "num_faces": 0,
                "faces": []
            }

        # Multi-face handling
        if len(faces) > 1 and selected_face_index is None:
            face_dicts = [f.to_dict() for f in faces]
            return {
                "status": "MULTIPLE_FACES_DETECTED",
                "message": f"Detected {len(faces)} faces. Please choose which face to analyze, or upload a photo with a single person.",
                "num_faces": len(faces),
                "faces": face_dicts
            }

        # Select target face
        target_idx = 0
        if selected_face_index is not None and 0 <= selected_face_index < len(faces):
            target_idx = selected_face_index
        face = faces[target_idx]

        # Quality assessment
        quality = assess_face_quality(image_rgb, face.box)

        # 5-point alignment
        aligned_112 = align_face_5point(image_rgb, face.landmarks, output_size=112)

        # Embedding generation
        embedding = self.model.generate_embedding(aligned_112)
        subfeatures = self.model.extract_subfeatures(aligned_112)

        return {
            "status": "SUCCESS",
            "message": "Face detected and processed successfully.",
            "num_faces": len(faces),
            "selected_face": face.to_dict(),
            "quality": quality,
            "embedding": embedding,
            "subfeatures": subfeatures,
            "aligned_face_rgb": aligned_112,
            "model_info": self.get_model_info()
        }

# Global singleton
vision_adapter = FaceModelAdapter()
