import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class GalleryParticipant(Base):
    __tablename__ = "gallery_participants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    display_name = Column(String(100), nullable=False)
    bio_caption = Column(String(255), nullable=True)
    consent_status = Column(String(50), default="synthetic_authorized")
    source = Column(String(100), default="Doppelganger Studio")
    license = Column(String(100), default="CC0-1.0")
    created_at = Column(DateTime, default=datetime.utcnow)

    images = relationship("GalleryImage", back_populates="participant", cascade="all, delete-orphan")

class GalleryImage(Base):
    __tablename__ = "gallery_images"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    participant_id = Column(String(36), ForeignKey("gallery_participants.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    image_url = Column(String(512), nullable=False)
    quality_score = Column(Float, default=1.0)
    is_primary = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    participant = relationship("GalleryParticipant", back_populates="images")
    embeddings = relationship("GalleryEmbedding", back_populates="image", cascade="all, delete-orphan")

class GalleryEmbedding(Base):
    __tablename__ = "gallery_embeddings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_id = Column(String(36), ForeignKey("gallery_images.id"), nullable=False)
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(50), nullable=False)
    dimension = Column(Float, nullable=False)
    embedding_bytes = Column(LargeBinary, nullable=False)
    subfeatures_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("GalleryImage", back_populates="embeddings")
