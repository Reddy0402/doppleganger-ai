from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FaceBox(BaseModel):
    box: List[int] = Field(..., description="[x, y, width, height]")
    confidence: float
    landmarks: List[List[float]] = Field(..., description="5 facial landmarks [[x, y], ...]")

class QualityAssessment(BaseModel):
    is_acceptable: bool
    overall_quality_score: float
    sharpness: Optional[float] = None
    mean_luminance: Optional[float] = None
    face_area_ratio: Optional[float] = None
    warnings: List[str] = []

class SubfeatureScore(BaseModel):
    score: float
    raw_cosine: float
    label: str

class MatchCandidate(BaseModel):
    rank: int
    participant_id: str
    display_name: str
    bio_caption: Optional[str] = None
    image_id: str
    image_url: str
    quality_score: float
    license_info: str
    consent_status: str
    similarity_score: float
    resemblance_percentage: float
    resemblance_tier: str
    badge_color: str
    description: str
    subfeature_breakdown: Optional[Dict[str, SubfeatureScore]] = None
    fun_caption: Optional[str] = None

class TierCounts(BaseModel):
    exceptional: int = 0
    strong: int = 0
    moderate: int = 0
    subtle: int = 0

class SearchStats(BaseModel):
    total_participants_searched: int
    total_portraits_indexed: int
    total_qualifying: int
    resemblance_threshold: float
    tier_counts: TierCounts
    detector: str
    recognition_model: str
    search_duration_ms: float

class MatchResponse(BaseModel):
    request_id: str
    status: str
    message: str
    num_faces_detected: int = 0
    detected_faces: List[FaceBox] = []
    selected_face_index: Optional[int] = None
    quality: Optional[QualityAssessment] = None
    matches: List[MatchCandidate] = []
    stats: Optional[SearchStats] = None
    model_name: str
    model_version: str
    dimension: int
    execution_latency_ms: float

