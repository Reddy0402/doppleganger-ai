import os
import cv2
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

def normalize_l2(vector: np.ndarray) -> np.ndarray:
    """
    Safely normalizes vector to unit L2 length (||v|| = 1.0).
    Safely handles zero vectors without division by zero.
    """
    norm = np.linalg.norm(vector)
    if norm < 1e-12 or np.isnan(norm):
        return np.zeros_like(vector, dtype=np.float32)
    return (vector / norm).astype(np.float32)

class BaseFaceModel(ABC):
    name: str = "base"
    version: str = "1.0.0"
    dimension: int = 128

    @abstractmethod
    def load_model(self) -> bool:
        pass

    @abstractmethod
    def generate_embedding(self, aligned_face_rgb: np.ndarray) -> np.ndarray:
        """Takes a 112x112 RGB aligned face crop, returns a 1D float32 normalized embedding."""
        pass

    @abstractmethod
    def extract_subfeatures(self, aligned_face_rgb: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extracts localized region embeddings:
        - eyes: upper orbital region
        - midface: nasal bridge
        - jawline: lower facial contour
        """
        pass

class SFaceModel(BaseFaceModel):
    name: str = "sface"
    version: str = "2021dec"
    dimension: int = 128

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or os.path.join("data", "models", "face_recognition_sface_2021dec.onnx")
        self.recognizer = None
        self.load_model()

    def load_model(self) -> bool:
        if os.path.exists(self.model_path):
            try:
                self.recognizer = cv2.FaceRecognizerSF.create(self.model_path, "")
                return True
            except Exception as e:
                print(f"[WARN] Failed to load SFace model from {self.model_path}: {e}")
                self.recognizer = None
        return False

    def generate_embedding(self, aligned_face_rgb: np.ndarray) -> np.ndarray:
        if self.recognizer is None:
            # Fallback if model not loaded
            return DeterministicBaselineModel().generate_embedding(aligned_face_rgb)

        # SFace expects 112x112 BGR image
        aligned_bgr = cv2.cvtColor(aligned_face_rgb, cv2.COLOR_RGB2BGR)
        raw_feat = self.recognizer.feature(aligned_bgr)
        flat = raw_feat.flatten().astype(np.float32)
        return normalize_l2(flat)

    def extract_subfeatures(self, aligned_face_rgb: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract region-specific embeddings by cropping canonical regions of 112x112 aligned face.
        """
        # Upper face (eyes region): rows 25:70
        eyes_crop = cv2.resize(aligned_face_rgb[25:70, :], (112, 112))
        # Midface (nose region): rows 45:85, cols 25:87
        nose_crop = cv2.resize(aligned_face_rgb[45:85, 25:87], (112, 112))
        # Lower face (mouth & jawline): rows 65:112
        jaw_crop = cv2.resize(aligned_face_rgb[65:112, :], (112, 112))

        return {
            "eyes": self.generate_embedding(eyes_crop),
            "nose": self.generate_embedding(nose_crop),
            "jawline": self.generate_embedding(jaw_crop),
        }

class DeterministicBaselineModel(BaseFaceModel):
    """
    Reproducible spatial-gradient feature extractor for testing or offline environments.
    Guarantees deterministic, reproducible, unit-normalized 128D embeddings.
    """
    name: str = "deterministic_baseline"
    version: str = "1.0.0"
    dimension: int = 128

    def load_model(self) -> bool:
        return True

    def generate_embedding(self, aligned_face_rgb: np.ndarray) -> np.ndarray:
        # Resize to fixed grid
        resized = cv2.resize(aligned_face_rgb, (64, 64))
        gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY).astype(np.float32)
        
        # Compute multi-scale Sobel gradients
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag = np.sqrt(gx**2 + gy**2)
        
        # Block pooling into 128 dimensions (8x16 spatial cells)
        cell_h, cell_w = 8, 4
        cells = []
        for i in range(8):
            for j in range(16):
                cell = mag[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                cells.append(np.mean(cell))
        
        vec = np.array(cells, dtype=np.float32)
        return normalize_l2(vec)

    def extract_subfeatures(self, aligned_face_rgb: np.ndarray) -> Dict[str, np.ndarray]:
        eyes_crop = cv2.resize(aligned_face_rgb[25:70, :], (112, 112))
        nose_crop = cv2.resize(aligned_face_rgb[45:85, 25:87], (112, 112))
        jaw_crop = cv2.resize(aligned_face_rgb[65:112, :], (112, 112))
        return {
            "eyes": self.generate_embedding(eyes_crop),
            "nose": self.generate_embedding(nose_crop),
            "jawline": self.generate_embedding(jaw_crop),
        }
