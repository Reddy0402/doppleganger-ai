import os
import cv2
import numpy as np
from typing import List, Dict, Any, Optional

class FaceObject:
    def __init__(
        self,
        box: List[int],
        confidence: float,
        landmarks: List[List[float]],
        raw_detection: Optional[np.ndarray] = None
    ):
        self.box = box  # [x, y, w, h]
        self.confidence = confidence
        self.landmarks = landmarks  # [[x, y], ...] 5 points
        self.raw_detection = raw_detection  # 15-dim vector for FaceRecognizerSF

    def to_dict(self) -> Dict[str, Any]:
        return {
            "box": self.box,
            "confidence": round(float(self.confidence), 4),
            "landmarks": [[round(float(c), 1) for c in pt] for pt in self.landmarks]
        }

class FaceDetector:
    def __init__(self, model_path: Optional[str] = None, score_threshold: float = 0.6, nms_threshold: float = 0.3):
        self.model_path = model_path or os.path.join("data", "models", "face_detection_yunet_2023mar.onnx")
        self.score_threshold = score_threshold
        self.nms_threshold = nms_threshold
        self.yunet = None
        self._load_detector()

    def _load_detector(self):
        if os.path.exists(self.model_path):
            try:
                # YuNet requires initial size (width, height)
                self.yunet = cv2.FaceDetectorYN.create(
                    model=self.model_path,
                    config="",
                    input_size=(320, 320),
                    score_threshold=self.score_threshold,
                    nms_threshold=self.nms_threshold,
                    top_k=10
                )
            except Exception as e:
                print(f"[WARN] Failed to initialize YuNet from {self.model_path}: {e}")
                self.yunet = None

    def detect(self, image_rgb: np.ndarray) -> List[FaceObject]:
        """
        Detects faces in an RGB image.
        Returns a list of FaceObject instances ordered by confidence * bounding box area.
        """
        h, w = image_rgb.shape[:2]
        
        # 1. Try YuNet deep detector
        if self.yunet is not None:
            try:
                # Convert RGB to BGR for OpenCV
                image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
                self.yunet.setInputSize((w, h))
                _, faces = self.yunet.detect(image_bgr)
                
                if faces is not None and len(faces) > 0:
                    results = []
                    for raw in faces:
                        box = [int(raw[0]), int(raw[1]), int(raw[2]), int(raw[3])]
                        conf = float(raw[14])
                        # 5 landmarks: right_eye, left_eye, nose, right_mouth, left_mouth
                        landmarks = [
                            [float(raw[4]), float(raw[5])],
                            [float(raw[6]), float(raw[7])],
                            [float(raw[8]), float(raw[9])],
                            [float(raw[10]), float(raw[11])],
                            [float(raw[12]), float(raw[13])],
                        ]
                        results.append(FaceObject(box, conf, landmarks, raw_detection=raw))
                    
                    # Sort by bounding box area * confidence descending
                    results.sort(key=lambda f: (f.box[2] * f.box[3]) * f.confidence, reverse=True)
                    return results
            except Exception as e:
                print(f"[WARN] YuNet inference error: {e}. Falling back to cascade.")

        # 2. Fallback: OpenCV Haar Cascade
        return self._detect_haar_fallback(image_rgb)

    def _detect_haar_fallback(self, image_rgb: np.ndarray) -> List[FaceObject]:
        gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if not os.path.exists(cascade_path):
            return []
            
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces_detected = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
        
        results = []
        for (x, y, bw, bh) in faces_detected:
            # Approximate 5 landmarks based on canonical facial geometry
            right_eye = [float(x + 0.35 * bw), float(y + 0.35 * bh)]
            left_eye = [float(x + 0.65 * bw), float(y + 0.35 * bh)]
            nose = [float(x + 0.5 * bw), float(y + 0.55 * bh)]
            right_mouth = [float(x + 0.35 * bw), float(y + 0.75 * bh)]
            left_mouth = [float(x + 0.65 * bw), float(y + 0.75 * bh)]
            landmarks = [right_eye, left_eye, nose, right_mouth, left_mouth]
            
            raw = np.array([x, y, bw, bh,
                            right_eye[0], right_eye[1],
                            left_eye[0], left_eye[1],
                            nose[0], nose[1],
                            right_mouth[0], right_mouth[1],
                            left_mouth[0], left_mouth[1],
                            0.85], dtype=np.float32)
            results.append(FaceObject([int(x), int(y), int(bw), int(bh)], 0.85, landmarks, raw_detection=raw))
            
        results.sort(key=lambda f: f.box[2] * f.box[3], reverse=True)
        return results
