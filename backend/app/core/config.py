import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Doppelgänger AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "https://doppleganger-ai.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Vision & Models
    DEFAULT_MODEL: str = "sface"  # "sface", "arcface_onnx", "deterministic"
    MODELS_DIR: str = os.path.join("data", "models")
    YUNET_MODEL_PATH: str = os.path.join("data", "models", "face_detection_yunet_2023mar.onnx")
    SFACE_MODEL_PATH: str = os.path.join("data", "models", "face_recognition_sface_2021dec.onnx")
    
    # Storage & Upload Security
    UPLOAD_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
    MAX_IMAGE_DIMENSION: int = 4096            # Prevent decompression bomb
    MIN_FACE_SIZE_PX: int = 60                 # Minimum face size for valid detection
    TEMP_UPLOAD_DIR: str = os.path.join("backend", "temp")
    GALLERY_DIR: str = os.path.join("data", "demo_gallery")
    DATABASE_URL: str = "sqlite:///./data/doppelganger.db"
    
    # Privacy
    EPHEMERAL_CLEANUP_SECONDS: int = 300       # Wipe uploads older than 5 mins
    
    # Optional GenAI
    GEMINI_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"
    
    model_config = {
        "env_file": ".env",
        "extra": "allow"
    }

settings = Settings()
