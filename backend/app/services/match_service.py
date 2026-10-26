import os
import time
import json
import uuid
import numpy as np
from typing import Dict, Any, Optional

from backend.app.core.config import settings
from backend.app.core.security import validate_image_file, load_and_preprocess_image, ephemeral_manager
from backend.app.vision.adapter import vision_adapter
from backend.app.retrieval.vector_index import gallery_index, GalleryRecord
from backend.app.services.genai_service import generate_fun_caption

def init_gallery_index():
    """
    Loads precomputed embeddings and metadata from disk on application startup.
    Takes <10ms for instantaneous server readiness.
    """
    model_info = vision_adapter.get_model_info()
    npy_path = os.path.join(settings.GALLERY_DIR, f"embeddings_{model_info['name']}.npy")
    meta_path = os.path.join(settings.GALLERY_DIR, "index_meta.json")

    if not os.path.exists(npy_path) or not os.path.exists(meta_path):
        print(f"[INFO] Precomputed gallery index not found at {npy_path}. Gallery is currently empty.")
        return

    try:
        matrix = np.load(npy_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        records = []
        for idx, rec in enumerate(meta.get("records", [])):
            sub_np = {k: np.array(v, dtype=np.float32) for k, v in rec.get("subfeatures", {}).items()}
            records.append(GalleryRecord(
                image_id=rec["image_id"],
                participant_id=rec["participant_id"],
                display_name=rec["display_name"],
                bio_caption=rec.get("bio_caption", ""),
                image_url=rec.get("image_url", ""),
                embedding=matrix[idx],
                subfeatures=sub_np,
                quality_score=rec.get("quality_score", 1.0),
                license_info=rec.get("license_info", "CC0-1.0"),
                consent_status=rec.get("consent_status", "synthetic_authorized")
            ))

        gallery_index.clear()
        gallery_index.dimension = model_info["dimension"]
        gallery_index.add_records(records)
        print(f"[OK] Gallery index initialized with {len(records)} portraits.")
    except Exception as e:
        print(f"[WARN] Failed to load cached gallery index: {e}")

def process_match_request(
    file_bytes: bytes,
    top_k: Optional[int] = None,
    min_threshold: float = 0.0,
    selected_face_index: Optional[int] = None,
    aggregation_policy: str = "max"
) -> Dict[str, Any]:
    req_id = str(uuid.uuid4())
    t0 = time.perf_counter()

    # 1. Security & File Format Validation
    valid, err_msg, mime = validate_image_file(file_bytes, max_bytes=settings.UPLOAD_MAX_BYTES)
    if not valid:
        return {
            "request_id": req_id,
            "status": "INVALID_IMAGE",
            "message": err_msg,
            "execution_latency_ms": round((time.perf_counter() - t0) * 1000.0, 2),
            "matches": []
        }

    # 2. Decode and Preprocess Image (EXIF orientation, RGB, max dimensions)
    try:
        img_rgb, original_dims = load_and_preprocess_image(file_bytes, max_dimension=settings.MAX_IMAGE_DIMENSION)
    except Exception as e:
        return {
            "request_id": req_id,
            "status": "PROCESSING_ERROR",
            "message": f"Failed to decode image: {str(e)}",
            "execution_latency_ms": round((time.perf_counter() - t0) * 1000.0, 2),
            "matches": []
        }

    # 3. Vision Pipeline (Detection, Quality, Alignment, Embeddings)
    model_info = vision_adapter.get_model_info()
    proc = vision_adapter.process_image(img_rgb, selected_face_index=selected_face_index)

    if proc["status"] != "SUCCESS":
        return {
            "request_id": req_id,
            "status": proc["status"],
            "message": proc["message"],
            "num_faces_detected": proc.get("num_faces", 0),
            "detected_faces": proc.get("faces", []),
            "model_name": model_info["name"],
            "model_version": model_info["version"],
            "dimension": model_info["dimension"],
            "execution_latency_ms": round((time.perf_counter() - t0) * 1000.0, 2),
            "matches": []
        }

    # 4. Vector Search against Complete Authorized Gallery
    query_emb = proc["embedding"]
    query_sub = proc["subfeatures"]
    quality_info = proc["quality"]
    
    t_search_0 = time.perf_counter()
    search_output = gallery_index.search(
        query_vec=query_emb,
        query_subfeatures=query_sub,
        top_k=top_k,
        min_threshold=min_threshold,
        aggregation_policy=aggregation_policy
    )
    search_duration_ms = round((time.perf_counter() - t_search_0) * 1000.0, 2)

    matches = search_output["matches"]

    # Enrich with fun captions
    for m in matches:
        m["fun_caption"] = generate_fun_caption(m["display_name"], m["resemblance_percentage"])

    total_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    stats = {
        "total_participants_searched": search_output["total_participants_searched"],
        "total_portraits_indexed": search_output["total_portraits_indexed"],
        "total_qualifying": search_output["total_qualifying"],
        "resemblance_threshold": min_threshold,
        "tier_counts": search_output["tier_counts"],
        "detector": model_info.get("detector", "yunet_2023mar"),
        "recognition_model": f"{model_info['name']} v{model_info['version']}",
        "search_duration_ms": search_duration_ms
    }

    return {
        "request_id": req_id,
        "status": "SUCCESS",
        "message": f"Successfully retrieved {len(matches)} doppelgänger matches (out of {search_output['total_qualifying']} qualifying unique participants).",
        "num_faces_detected": proc["num_faces"],
        "detected_faces": [proc["selected_face"]],
        "selected_face_index": selected_face_index or 0,
        "quality": quality_info,
        "matches": matches,
        "stats": stats,
        "model_name": model_info["name"],
        "model_version": model_info["version"],
        "dimension": model_info["dimension"],
        "execution_latency_ms": total_time_ms
    }
