import os
import json
import base64
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.security import ephemeral_manager
from backend.app.database.db import get_db
from backend.app.database.models import GalleryParticipant, GalleryImage
from backend.app.vision.adapter import vision_adapter
from backend.app.retrieval.vector_index import gallery_index
from backend.app.services.match_service import process_match_request, init_gallery_index
from backend.app.schemas.matches import MatchResponse
from backend.app.schemas.gallery import GalleryListResponse, ParticipantDetail, GalleryImageItem
from backend.app.schemas.evaluation import EvaluationSummaryResponse

router = APIRouter()

@router.get("/health")
def get_health():
    model_info = vision_adapter.get_model_info()
    return {
        "status": "online",
        "service": "Doppelgänger AI API",
        "version": settings.VERSION,
        "active_model": model_info["name"],
        "model_version": model_info["version"],
        "dimension": model_info["dimension"],
        "detector": model_info["detector"],
        "gallery_portraits_count": len(gallery_index.records)
    }

@router.get("/models")
def list_models():
    model_info = vision_adapter.get_model_info()
    return {
        "active_model": model_info["name"],
        "active_info": model_info,
        "available_models": [
            {
                "name": "sface",
                "display_name": "SFace (ArcFace-based)",
                "description": "Pretrained deep ArcFace feature extractor with 5-point canonical alignment.",
                "dimension": 128,
                "license": "Apache-2.0"
            },
            {
                "name": "deterministic",
                "display_name": "Deterministic Baseline Extractor",
                "description": "Reproducible spatial-gradient pooling extractor for offline verification.",
                "dimension": 128,
                "license": "MIT"
            }
        ]
    }

@router.post("/models/select")
def select_model(model_name: str = Form(...)):
    if model_name not in ["sface", "deterministic"]:
        raise HTTPException(status_code=400, detail="Unsupported model.")
    vision_adapter.set_model(model_name)
    init_gallery_index()
    return {"status": "success", "active_model": model_name}

@router.get("/gallery/stats")
def get_gallery_stats(db: Session = Depends(get_db)):
    """
    Returns unique participant count and indexed portrait count.
    """
    unique_count = db.query(GalleryParticipant).count()
    portrait_count = db.query(GalleryImage).count()
    return {
        "unique_participants": unique_count,
        "indexed_portraits": portrait_count,
        "cached_index_portraits": len(gallery_index.records)
    }

@router.post("/gallery/reindex")
def reindex_gallery(db: Session = Depends(get_db)):
    """
    Rebuild the gallery vector index and synchronize database records.
    """
    from backend.scripts.ingest_gallery import ingest_gallery
    success = ingest_gallery()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reindex gallery.")
    init_gallery_index()
    unique_count = db.query(GalleryParticipant).count()
    portrait_count = db.query(GalleryImage).count()
    return {
        "status": "success",
        "message": f"Gallery reindexed successfully. {unique_count} unique participants, {portrait_count} portraits.",
        "unique_participants": unique_count,
        "indexed_portraits": portrait_count
    }

@router.post("/matches")
async def find_matches(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
    top_k: Optional[int] = Form(None),
    min_threshold: float = Form(0.0),
    selected_face_index: Optional[int] = Form(None),
    aggregation_policy: str = Form("max")
):
    file_bytes = b""
    if file is not None:
        file_bytes = await file.read()
    elif image_base64 is not None:
        # Support camera data URL (e.g. data:image/jpeg;base64,...)
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        try:
            file_bytes = base64.b64decode(image_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 image data.")
    else:
        raise HTTPException(status_code=400, detail="No image file or camera capture was provided.")

    response = process_match_request(
        file_bytes=file_bytes,
        top_k=top_k,
        min_threshold=min_threshold,
        selected_face_index=selected_face_index,
        aggregation_policy=aggregation_policy
    )
    return response

@router.get("/gallery")
def get_gallery(
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(GalleryParticipant)
    total_participants = query.count()
    total_images = db.query(GalleryImage).count()

    offset = max(0, (page - 1) * page_size)
    participants = query.offset(offset).limit(page_size).all()

    results = []
    for p in participants:
        img_items = []
        for img in p.images:
            img_items.append(GalleryImageItem(
                id=img.id,
                filename=img.filename,
                image_url=img.image_url,
                quality_score=img.quality_score,
                is_primary=img.is_primary
            ))
        results.append(ParticipantDetail(
            id=p.id,
            display_name=p.display_name,
            bio_caption=p.bio_caption,
            consent_status=p.consent_status,
            source=p.source,
            license=p.license,
            images=img_items
        ))

    model_info = vision_adapter.get_model_info()
    return {
        "total_participants": total_participants,
        "total_images": total_images,
        "page": page,
        "page_size": page_size,
        "active_model": model_info["name"],
        "participants": results
    }

@router.get("/gallery/{participant_id}")
def get_participant(participant_id: str, db: Session = Depends(get_db)):
    p = db.query(GalleryParticipant).filter_by(id=participant_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found.")
    
    img_items = [
        GalleryImageItem(
            id=img.id,
            filename=img.filename,
            image_url=img.image_url,
            quality_score=img.quality_score,
            is_primary=img.is_primary
        ) for img in p.images
    ]
    return ParticipantDetail(
        id=p.id,
        display_name=p.display_name,
        bio_caption=p.bio_caption,
        consent_status=p.consent_status,
        source=p.source,
        license=p.license,
        images=img_items
    )

@router.get("/gallery/images/{filename}")
def get_gallery_image(filename: str):
    # Sanitize filename
    safe_name = os.path.basename(filename)
    filepath = os.path.join(settings.GALLERY_DIR, "images", safe_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found.")
    
    media_type = "image/jpeg"
    if safe_name.lower().endswith(".png"):
        media_type = "image/png"
    elif safe_name.lower().endswith(".webp"):
        media_type = "image/webp"

    return FileResponse(filepath, media_type=media_type)

@router.delete("/uploads/{upload_id}")
def delete_upload(upload_id: str):
    """
    Explicit biometric privacy endpoint allowing users to purge their session upload data immediately.
    """
    success = ephemeral_manager.delete_file(upload_id)
    return {
        "status": "success" if success else "not_found",
        "message": "Temporary upload purged." if success else "No retained session upload found (ephemeral files are wiped automatically)."
    }

@router.get("/evaluation/summary")
def get_evaluation_summary():
    metrics_path = os.path.join("data", "evaluation", "metrics.json")
    if not os.path.exists(metrics_path):
        raise HTTPException(status_code=404, detail="Evaluation metrics not yet computed.")
    
    with open(metrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
