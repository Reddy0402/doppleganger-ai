import io
import os
import uuid
import time
import shutil
from typing import Tuple, Optional
from PIL import Image, ImageOps
import numpy as np

# Magic byte signatures for image formats
MAGIC_NUMBERS = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp"
}

def validate_image_file(file_bytes: bytes, max_bytes: int = 10 * 1024 * 1024) -> Tuple[bool, str, Optional[str]]:
    """
    Validate raw file bytes:
    - Check size limit
    - Check magic bytes for JPEG, PNG, WebP
    - Open with PIL to ensure not truncated or corrupt
    """
    if len(file_bytes) == 0:
        return False, "Uploaded file is empty.", None
        
    if len(file_bytes) > max_bytes:
        mb = max_bytes / (1024 * 1024)
        return False, f"File size exceeds maximum permitted limit ({mb:.1f} MB).", None

    # Magic byte check
    detected_mime = None
    if file_bytes.startswith(b"\xff\xd8\xff"):
        detected_mime = "image/jpeg"
    elif file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        detected_mime = "image/png"
    elif file_bytes[:4] == b"RIFF" and len(file_bytes) >= 12 and file_bytes[8:12] == b"WEBP":
        detected_mime = "image/webp"

    if not detected_mime:
        return False, "Unsupported file format. Please upload a valid JPEG, PNG, or WebP image.", None

    # Deep format validation using PIL
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
    except Exception as e:
        return False, f"Image file is corrupt or unreadable: {str(e)}", None

    return True, "Valid", detected_mime

def load_and_preprocess_image(file_bytes: bytes, max_dimension: int = 4096) -> Tuple[np.ndarray, Tuple[int, int]]:
    """
    Load image, apply EXIF orientation transpose, enforce max dimensions to prevent decompression bombs,
    convert to RGB, and return RGB numpy array (H, W, 3) and original dimensions (W, H).
    """
    with Image.open(io.BytesIO(file_bytes)) as pil_img:
        # EXIF orientation correction
        pil_img = ImageOps.exif_transpose(pil_img)
        
        # Ensure RGB
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
            
        w, h = pil_img.size
        # Resize if dimensions exceed threshold
        if max(w, h) > max_dimension:
            scale = max_dimension / max(w, h)
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            w, h = new_w, new_h

        img_np = np.array(pil_img)
        return img_np, (w, h)

class EphemeralStorageManager:
    """
    Manages temporary uploads and securely purges files after session or expiration.
    Guarantees privacy by ensuring no persistent selfie files remain on disk.
    """
    def __init__(self, temp_dir: str = "backend/temp", max_age_seconds: int = 300):
        self.temp_dir = temp_dir
        self.max_age_seconds = max_age_seconds
        os.makedirs(self.temp_dir, exist_ok=True)

    def create_temp_path(self, suffix: str = ".jpg") -> Tuple[str, str]:
        file_id = str(uuid.uuid4())
        filename = f"upload_{file_id}{suffix}"
        filepath = os.path.join(self.temp_dir, filename)
        return file_id, filepath

    def delete_file(self, filepath_or_id: str) -> bool:
        try:
            if os.path.exists(filepath_or_id):
                os.remove(filepath_or_id)
                return True
            # Search by ID in temp_dir
            for f in os.listdir(self.temp_dir):
                if filepath_or_id in f:
                    os.remove(os.path.join(self.temp_dir, f))
                    return True
        except Exception:
            pass
        return False

    def cleanup_expired(self):
        """Purge any files older than max_age_seconds"""
        now = time.time()
        try:
            for fname in os.listdir(self.temp_dir):
                fpath = os.path.join(self.temp_dir, fname)
                if os.path.isfile(fpath):
                    if now - os.path.getmtime(fpath) > self.max_age_seconds:
                        try:
                            os.remove(fpath)
                        except Exception:
                            pass
        except Exception:
            pass

ephemeral_manager = EphemeralStorageManager()
