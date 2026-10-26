import os
import sys
import argparse
import json
import shutil
import cv2
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.database.db import SessionLocal, init_db
from backend.app.database.models import GalleryParticipant, GalleryImage, GalleryEmbedding
from backend.app.vision.adapter import vision_adapter
from backend.app.core.config import settings

def ingest_dataset(
    source_dir: str,
    dataset_name: str = "CelebA-HQ",
    max_images: int = 500,
    min_quality: float = 0.35,
    license_tag: str = "Non-commercial Research",
    copy_to_gallery: bool = True
):
    """
    Ingests an external dataset directory (e.g. CelebAMask-HQ, CelebA-Spoof, InsightFace aligned crops, Talk-to-Edit)
    into Doppelgänger AI's gallery index and database.
    
    1. Discovers image files in source_dir (.jpg, .jpeg, .png, .webp).
    2. Runs YuNet face detection, canonical 5-point alignment, quality assessment.
    3. Filters out low-quality/undetected faces.
    4. Extracts ArcFace/SFace 128D embeddings and orbital/nasal/jawline subfeatures.
    5. Stores records in SQLite DB and updates index_meta.json & embeddings_sface.npy.
    """
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"[ERROR] Source directory does not exist: {source_dir}")
        return False

    print("=" * 70)
    print(f"      DOPPELGÄNGER AI: DATASET INGESTION ({dataset_name})")
    print(f"      Source: {source_path}")
    print(f"      Max Images: {max_images} | Min Quality Score: {min_quality}")
    print("=" * 70)

    init_db()
    db = SessionLocal()

    target_images_dir = Path(settings.GALLERY_DIR) / "images"
    target_images_dir.mkdir(parents=True, exist_ok=True)

    # Supported image formats
    valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
    candidate_files = []
    for root, _, files in os.walk(source_path):
        for f in files:
            if Path(f).suffix.lower() in valid_exts:
                candidate_files.append(Path(root) / f)
                if len(candidate_files) >= max_images * 2:
                    break
        if len(candidate_files) >= max_images * 2:
            break

    print(f"[INFO] Scanned and found {len(candidate_files)} image candidates.")
    if not candidate_files:
        print("[WARN] No valid images found in source path.")
        db.close()
        return False

    # Existing gallery records to merge with
    meta_path = os.path.join(settings.GALLERY_DIR, "index_meta.json")
    npy_path = os.path.join(settings.GALLERY_DIR, f"embeddings_{vision_adapter.active_model_name}.npy")

    cached_records = []
    cached_matrix = []
    existing_img_ids = set()

    if os.path.exists(meta_path) and os.path.exists(npy_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                existing_meta = json.load(f)
            cached_records = existing_meta.get("records", [])
            cached_matrix = [rec for rec in np.load(npy_path)]
            existing_img_ids = {r["image_id"] for r in cached_records}
            print(f"[INFO] Loaded {len(cached_records)} existing gallery records to append into.")
        except Exception as e:
            print(f"[WARN] Failed to load existing index cache: {e}. Starting fresh.")
            cached_records = []
            cached_matrix = []

    model_info = vision_adapter.get_model_info()
    processed_count = 0
    success_count = 0
    failed_count = 0

    for file_path in candidate_files:
        if success_count >= max_images:
            print(f"[INFO] Reached target limit of {max_images} successfully indexed faces.")
            break

        processed_count += 1
        base_name = file_path.stem
        # Derive identity and participant ID
        # Common naming: '00001.jpg', 'p_001_1.jpg', or identity folder name
        parent_name = file_path.parent.name
        if parent_name and parent_name.isdigit():
            p_id = f"p_{dataset_name.lower()}_{parent_name}"
            display_name = f"{dataset_name} ID #{parent_name}"
        else:
            p_id = f"p_{dataset_name.lower()}_{base_name}"
            display_name = f"{dataset_name} #{base_name}"

        dest_filename = f"{dataset_name.lower()}_{file_path.name}"
        dest_filepath = target_images_dir / dest_filename
        img_id = f"img_{dataset_name.lower()}_{base_name}"

        if img_id in existing_img_ids:
            continue

        # Load image
        img_bgr = cv2.imread(str(file_path))
        if img_bgr is None:
            failed_count += 1
            continue

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # Run vision detection, quality, and embedding pipeline
        try:
            process_res = vision_adapter.process_image(img_rgb)
        except Exception as e:
            failed_count += 1
            continue

        if process_res["status"] != "SUCCESS":
            failed_count += 1
            continue

        quality = process_res.get("quality", {})
        overall_quality = quality.get("overall_quality_score", 0.0)

        # Filter out blurry or poor quality images
        if overall_quality < min_quality:
            failed_count += 1
            continue

        embedding = process_res["embedding"]
        subfeatures = process_res["subfeatures"]
        sub_serialized = {k: v.tolist() for k, v in subfeatures.items()}

        # Copy image to gallery storage if requested
        if copy_to_gallery and not dest_filepath.exists():
            shutil.copy2(str(file_path), str(dest_filepath))
        relative_url = f"/api/gallery/images/{dest_filename}"

        # DB operations
        db_p = db.query(GalleryParticipant).filter_by(id=p_id).first()
        if not db_p:
            db_p = GalleryParticipant(
                id=p_id,
                display_name=display_name,
                bio_caption=f"Verified facial profile from {dataset_name} dataset.",
                consent_status="dataset_authorized",
                source=dataset_name,
                license=license_tag
            )
            db.add(db_p)
            db.commit()

        db_img = db.query(GalleryImage).filter_by(id=img_id).first()
        if not db_img:
            db_img = GalleryImage(
                id=img_id,
                participant_id=p_id,
                filename=dest_filename,
                file_path=str(dest_filepath),
                image_url=relative_url,
                quality_score=overall_quality,
                is_primary=True
            )
            db.add(db_img)
            db.commit()

        db_emb = db.query(GalleryEmbedding).filter_by(image_id=img_id, model_name=model_info["name"]).first()
        if not db_emb:
            db_emb = GalleryEmbedding(
                id=f"emb_{img_id}",
                image_id=img_id,
                model_name=model_info["name"],
                model_version=model_info["version"],
                dimension=model_info["dimension"],
                embedding_bytes=embedding.tobytes(),
                subfeatures_json=json.dumps(sub_serialized)
            )
            db.add(db_emb)
            db.commit()

        cached_matrix.append(embedding)
        cached_records.append({
            "image_id": img_id,
            "participant_id": p_id,
            "display_name": display_name,
            "bio_caption": f"Verified facial profile from {dataset_name} dataset.",
            "image_url": relative_url,
            "quality_score": overall_quality,
            "license_info": license_tag,
            "consent_status": "dataset_authorized",
            "subfeatures": sub_serialized
        })
        existing_img_ids.add(img_id)
        success_count += 1

        if success_count % 25 == 0:
            print(f"[PROGRESS] Indexed {success_count}/{max_images} portraits (Processed: {processed_count})...")

    # Save updated cache matrices
    if cached_matrix:
        matrix_np = np.vstack(cached_matrix).astype(np.float32)
        np.save(npy_path, matrix_np)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "model_name": model_info["name"],
                "model_version": model_info["version"],
                "dimension": model_info["dimension"],
                "count": len(cached_records),
                "records": cached_records
            }, f, indent=2)

    db.close()
    print("=" * 70)
    print(f"INGESTION COMPLETE:")
    print(f"  Dataset:             {dataset_name}")
    print(f"  Candidates Checked:  {processed_count}")
    print(f"  Successfully Added:  {success_count}")
    print(f"  Filtered / Failed:   {failed_count}")
    print(f"  Total Gallery Size:  {len(cached_records)}")
    print("=" * 70)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest external face datasets into Doppelgänger AI.")
    parser.add_argument("--source", type=str, required=True, help="Path to directory containing face images")
    parser.add_argument("--dataset", type=str, default="CelebA", help="Name of dataset (e.g. CelebAMask-HQ, CelebA-Spoof, InsightFace)")
    parser.add_argument("--limit", type=int, default=500, help="Maximum number of images to ingest")
    parser.add_argument("--min_quality", type=float, default=0.35, help="Minimum quality score threshold (0.0 to 1.0)")
    parser.add_argument("--license", type=str, default="Non-commercial Research", help="Dataset license label")
    
    args = parser.parse_args()
    ingest_dataset(
        source_dir=args.source,
        dataset_name=args.dataset,
        max_images=args.limit,
        min_quality=args.min_quality,
        license_tag=args.license
    )
