from typing import List, Optional
from pydantic import BaseModel

class GalleryImageItem(BaseModel):
    id: str
    filename: str
    image_url: str
    quality_score: float
    is_primary: bool

class ParticipantDetail(BaseModel):
    id: str
    display_name: str
    bio_caption: Optional[str] = None
    consent_status: str
    source: str
    license: str
    images: List[GalleryImageItem] = []

class GalleryListResponse(BaseModel):
    total_participants: int
    total_images: int
    active_model: str
    participants: List[ParticipantDetail]
