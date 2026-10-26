import os
import sys
import json
import cv2
import numpy as np
from datetime import datetime

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.database.db import SessionLocal, init_db
from backend.app.database.models import GalleryParticipant, GalleryImage, GalleryEmbedding
from backend.app.vision.adapter import vision_adapter

def ingest_gallery(
    manifest_path: str = "data/demo_gallery/manifest.json",
    images_base_dir: str = "data/demo_gallery/images",
    output_cache_dir: str = "data/demo_gallery"
) -> bool:
    print("=" * 65)
    print("      DOPPELGÄNGER AI: GALLERY INGESTION PIPELINE")
    print("=" * 65)

    init_db()
    db = SessionLocal()

    participants = []
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        participants = manifest_data.get("participants", [])
        print(f"[INFO] Found {len(participants)} participants in manifest.")
    
    # Also discover any non-manifest images (e.g. CelebA, InsightFace, etc.)
    manifest_filenames = set()
    for p in participants:
        for img in p.get("images", []):
            manifest_filenames.add(img.get("filename"))

    discovered_files = []
    for root, _, files in os.walk(images_base_dir):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                rel_file = os.path.relpath(os.path.join(root, file), images_base_dir)
                if rel_file not in manifest_filenames:
                    discovered_files.append(rel_file)

    if discovered_files:
        print(f"[INFO] Discovered {len(discovered_files)} additional images outside manifest. Appending...")
        for fname in discovered_files:
            clean_name = os.path.splitext(os.path.basename(fname))[0]
            parts = clean_name.split("_")
            p_id = f"p_{parts[0]}_{parts[1]}" if len(parts) >= 2 else f"p_{clean_name}"
            display_name = f"{parts[0].capitalize()} #{parts[1]}" if len(parts) >= 2 else clean_name.capitalize()
            participants.append({
                "id": p_id,
                "display_name": display_name,
                "bio_caption": f"Authorized portrait {display_name}",
                "consent_status": "dataset_authorized",
                "license": "Non-commercial Research",
                "source": "External Dataset",
                "images": [{"filename": fname, "is_primary": True}]
            })
        print(f"[INFO] Appended {len(discovered_files)} images into gallery pipeline.")

    total_images = 0
    successful_images = 0
    failed_images = []
    
    cached_records = []
    cached_matrix = []

    model_info = vision_adapter.get_model_info()
    print(f"[INFO] Using active model: {model_info['name']} v{model_info['version']} ({model_info['dimension']}D)")

    for p_data in participants:
        p_id = p_data.get("id")
        display_name = p_data.get("display_name", "Anonymous")
        bio_caption = p_data.get("bio_caption", "")
        consent = p_data.get("consent_status", "synthetic_authorized")
        license_info = p_data.get("license", "CC0-1.0")
        source = p_data.get("source", "Demo Studio")

        # Check or create DB record
        db_p = db.query(GalleryParticipant).filter_by(id=p_id).first()
        if not db_p:
            db_p = GalleryParticipant(
                id=p_id,
                display_name=display_name,
                bio_caption=bio_caption,
                consent_status=consent,
                source=source,
                license=license_info
            )
            db.add(db_p)
            db.commit()

        for img_info in p_data.get("images", []):
            total_images += 1
            fname = img_info.get("filename")
            fpath = os.path.join(images_base_dir, fname)

            if not os.path.exists(fpath):
                print(f"[WARN] File not found: {fpath}")
                failed_images.append((fname, "File not found"))
                continue

            # Load image
            img_bgr = cv2.imread(fpath)
            if img_bgr is None:
                print(f"[WARN] Failed to decode image: {fpath}")
                failed_images.append((fname, "Decoding failure"))
                continue

            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            # Run vision pipeline
            process_res = vision_adapter.process_image(img_rgb)
            if process_res["status"] != "SUCCESS":
                print(f"[WARN] Vision failure for {fname}: {process_res['status']} - {process_res['message']}")
                failed_images.append((fname, process_res["status"]))
                continue

            embedding = process_res["embedding"]
            subfeatures = process_res["subfeatures"]
            quality = process_res["quality"]
            img_id = f"img_{p_id}_{fname.split('.')[0]}"

            # Subfeatures serialized
            sub_serialized = {k: v.tolist() for k, v in subfeatures.items()}

            # Upsert in DB
            db_img = db.query(GalleryImage).filter_by(id=img_id).first()
            if not db_img:
                db_img = GalleryImage(
                    id=img_id,
                    participant_id=p_id,
                    filename=fname,
                    file_path=fpath,
                    image_url=f"/api/gallery/images/{fname}",
                    quality_score=quality["overall_quality_score"],
                    is_primary=img_info.get("is_primary", True)
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

            # Cache memory record
            cached_matrix.append(embedding)
            cached_records.append({
                "image_id": img_id,
                "participant_id": p_id,
                "display_name": display_name,
                "bio_caption": bio_caption,
                "image_url": f"/api/gallery/images/{fname}",
                "quality_score": quality["overall_quality_score"],
                "license_info": license_info,
                "consent_status": consent,
                "subfeatures": sub_serialized
            })

            successful_images += 1
            print(f"[OK] Indexed {fname} (Participant: {display_name}, Quality: {quality['overall_quality_score']})")

    # Export fast cache files
    if cached_matrix:
        matrix_np = np.vstack(cached_matrix).astype(np.float32)
        npy_path = os.path.join(output_cache_dir, f"embeddings_{model_info['name']}.npy")
        json_path = os.path.join(output_cache_dir, "index_meta.json")
        
        np.save(npy_path, matrix_np)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "model_name": model_info["name"],
                "model_version": model_info["version"],
                "dimension": model_info["dimension"],
                "count": len(cached_records),
                "created_at": datetime.utcnow().isoformat(),
                "records": cached_records
            }, f, indent=2)

        print(f"[CACHE] Saved {len(cached_matrix)} embeddings to {npy_path}")
        print(f"[CACHE] Saved metadata to {json_path}")

    db.close()

    print("-" * 65)
    print(f"INGESTION COMPLETE:")
    print(f"  Total Images Attempted: {total_images}")
    print(f"  Successfully Indexed:   {successful_images}")
    print(f"  Failures:               {len(failed_images)}")
    if failed_images:
        for f, reason in failed_images:
            print(f"    - {f}: {reason}")
    print("-" * 65)
    return successful_images > 0

if __name__ == "__main__":
    ingest_gallery()
