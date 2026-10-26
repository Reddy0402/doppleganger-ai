import os
import sys
import io
import zipfile
import urllib.request
from pathlib import Path

# Project paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.scripts.ingest_external_dataset import ingest_dataset

CELEBA_ZIP_URL = "https://huggingface.co/datasets/Yuehao/celeba/resolve/main/img_align_celeba.zip"

def stream_download_and_extract_sample(
    zip_url: str = CELEBA_ZIP_URL,
    target_dir: str = "data/celeba_sample",
    max_images_to_extract: int = 150
):
    """
    Downloads CelebA zip stream and extracts the first `max_images_to_extract` images
    without needing to download the entire 1.4GB archive to disk if interrupted.
    """
    out_dir = Path(target_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print(f"      STREAMING CELEBA DATASET SAMPLE ({max_images_to_extract} images)")
    print(f"      Source: {zip_url}")
    print("=" * 65)

    req = urllib.request.Request(zip_url, headers={"User-Agent": "Mozilla/5.0"})
    
    # Download ~250MB to extract 1200+ images
    buffer = io.BytesIO()
    chunk_size = 1024 * 1024  # 1MB
    downloaded = 0
    max_download_bytes = 250 * 1024 * 1024  # 250 MB

    print(f"[INFO] Streaming ~250MB chunk of CelebA archive for 1200+ images...")
    with urllib.request.urlopen(req, timeout=120) as resp:
        while downloaded < max_download_bytes:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            buffer.write(chunk)
            downloaded += len(chunk)
            print(f"  [STREAM] Downloaded {downloaded // (1024*1024)} MB...", end="\r")

    print(f"\n[INFO] Finished download buffer: {downloaded / (1024*1024):.2f} MB.")
    
    # Unzip images from the buffer
    extracted_count = 0
    buffer.seek(0)
    try:
        with zipfile.ZipFile(buffer) as z:
            namelist = [n for n in z.namelist() if n.lower().endswith((".jpg", ".png", ".jpeg"))]
            print(f"[INFO] Found {len(namelist)} images inside downloaded chunk index.")
            for name in namelist[:max_images_to_extract]:
                data = z.read(name)
                fname = os.path.basename(name)
                out_path = out_dir / fname
                with open(out_path, "wb") as f:
                    f.write(data)
                extracted_count += 1
    except zipfile.BadZipFile:
        # If central directory is at end of zip, extract JPEG frames directly by scanning JPEG markers (0xFFD8 to 0xFFD9)
        print("[INFO] Scanning stream buffer for standard JPEG frames...")
        raw_bytes = buffer.getvalue()
        pos = 0
        img_idx = 0
        while pos < len(raw_bytes) and img_idx < max_images_to_extract:
            start = raw_bytes.find(b"\xff\xd8\xff", pos)
            if start == -1:
                break
            end = raw_bytes.find(b"\xff\xd9", start)
            if end == -1:
                break
            jpeg_data = raw_bytes[start : end + 2]
            if len(jpeg_data) > 5000:  # Valid face image
                out_path = out_dir / f"celeba_{img_idx:05d}.jpg"
                with open(out_path, "wb") as f:
                    f.write(jpeg_data)
                img_idx += 1
                extracted_count += 1
            pos = end + 2

    print(f"[OK] Extracted {extracted_count} CelebA facial portraits into {target_dir}")
    return extracted_count

if __name__ == "__main__":
    count = stream_download_and_extract_sample(max_images_to_extract=1300)
    if count > 0:
        print("[INFO] Running automated ingestion pipeline into Doppelgänger AI gallery...")
        ingest_dataset(
            source_dir="data/celeba_sample",
            dataset_name="CelebA",
            max_images=1300,
            min_quality=0.30
        )


