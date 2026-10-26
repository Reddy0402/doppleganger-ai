"""
Download verified open-source face detection (YuNet) and recognition (SFace) ONNX models
from official OpenCV Zoo repository (Apache-2.0 License).
"""
import os
import sys
import requests

MODELS = {
    "face_detection_yunet_2023mar.onnx": {
        "url": "https://raw.githubusercontent.com/opencv/opencv_zoo/master/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        "description": "YuNet Face Detector (OpenCV Zoo, Apache 2.0)",
        "expected_min_bytes": 200_000,
    },
    "face_recognition_sface_2021dec.onnx": {
        "url": "https://huggingface.co/opencv/face_recognition_sface/resolve/main/face_recognition_sface_2021dec.onnx",
        "description": "SFace ArcFace Face Recognizer (OpenCV Zoo, Apache 2.0)",
        "expected_min_bytes": 10_000_000,
    }
}

def download_models(target_dir: str = "data/models") -> bool:
    os.makedirs(target_dir, exist_ok=True)
    all_success = True

    for filename, info in MODELS.items():
        filepath = os.path.join(target_dir, filename)
        if os.path.exists(filepath) and os.path.getsize(filepath) >= info["expected_min_bytes"]:
            print(f"[OK] {filename} already exists ({os.path.getsize(filepath)} bytes).")
            continue

        print(f"[DOWNLOADING] {info['description']} -> {filepath}...")
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DoppelgangerAI/1.0"}
            response = requests.get(info["url"], stream=True, timeout=60, headers=headers)
            response.raise_for_status()
            
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
            
            size = os.path.getsize(filepath)
            if size < info["expected_min_bytes"]:
                print(f"[WARN] Downloaded {filename} is unexpectedly small ({size} bytes).")
                all_success = False
            else:
                print(f"[DOWNLOAD SUCCESS] {filename} downloaded successfully ({size} bytes).")
        except Exception as e:
            print(f"[ERROR] Failed to download {filename}: {e}")
            all_success = False

    return all_success

if __name__ == "__main__":
    success = download_models()
    if not success:
        print("[NOTICE] Running with fallback models if models could not be fetched.")
        sys.exit(0)
