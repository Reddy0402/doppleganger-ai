# Doppelgänger AI: System Architecture

## Overview
Doppelgänger AI is an end-to-end computer vision and similarity retrieval platform designed to identify perceptual visual lookalikes from an authorized portrait gallery. The system prioritizes measurable retrieval quality, ethical data management, and strict biometric privacy standards.

```
                              +-------------------------+
                              |   Client (React + TS)   |
                              +------------+------------+
                                           |
                                    HTTPS Multipart
                                           |
                                           v
                              +-------------------------+
                              |    FastAPI Gateway      |
                              +------------+------------+
                                           |
                                           v
    +-------------------------------------------------------------------------+
    |                        Computer Vision Pipeline                         |
    |                                                                         |
    | 1. Image Security & Validation (File magic, max 10MB, EXIF orient, RGB) |
    | 2. Quality Control (Blur/Laplacian, exposure, face scale ratio)         |
    | 3. Face Detection & Landmarking (OpenCV YuNet / SCRFD 5-point)          |
    | 4. Affine Landmark Alignment (112x112 standard canonical face frame)     |
    | 5. Deep Embedding Generation (ArcFace / SFace 128D / 512D)              |
    | 6. Unit L2 Normalization (||v|| = 1.0)                                  |
    +--------------------------------------+----------------------------------+
                                           |
                                           v
    +-------------------------------------------------------------------------+
    |                    Vector Retrieval & Ranking Engine                    |
    |                                                                         |
    | Mode A: Exact Cosine Similarity Baseline (NumPy dot product)            |
    | Mode B: FAISS IndexFlatIP / IndexHNSW (for scaled gallery search)        |
    | Candidate Filtering & Multi-Pose Aggregation (Max-similarity policy)    |
    | Optional Resemblance Calibration & Sub-feature Region Scores            |
    +--------------------------------------+----------------------------------+
                                           |
                                           v
    +-------------------------------------------------------------------------+
    |                        Response & Privacy Policy                        |
    |                                                                         |
    | Top-K Candidates, Perceptual Confidence, Sub-feature breakdowns         |
    | Ephemeral storage: uploaded user selfie wiped immediately after session |
    | Zero biometric embeddings retained without persistent consent            |
    +-------------------------------------------------------------------------+
```

## Core Modules

### 1. Vision Subsystem (`backend/app/vision/`)
- `detector.py`: Deep face detection using OpenCV YuNet DNN / Haar/SSD fallback. Extracts bounding box and 5 facial landmarks (right eye, left eye, nose tip, right mouth corner, left mouth corner).
- `alignment.py`: 5-point affine transformation aligning eyes horizontally and anchoring nose and mouth to standard 112x112 coordinates.
- `quality.py`: Image quality metrics:
  - Laplacian variance blur detection (`variance < threshold` indicates blur).
  - Luminance histogram exposure check (underexposed or washed out).
  - Face bounding box area percentage (minimum resolution threshold).
- `embeddings.py`: Model adapter interface (`BaseFaceModel`) supporting:
  - `SFaceModel`: Lightweight OpenCV DNN ArcFace-derived model (128D).
  - `ArcFaceONNXModel`: Deep ResNet50/MobileFaceNet ONNX ArcFace model (512D).
  - `DeterministicBaselineModel`: Fallback feature extractor for zero-network testing environments.
- `adapter.py`: Runtime model switcher preserving dimension checks and cache consistency.

### 2. Retrieval Subsystem (`backend/app/retrieval/`)
- `similarity.py`: Exact cosine similarity with zero-vector guard, dimension validation, and deterministic tie-breaking.
- `vector_index.py`: Index manager supporting both in-memory NumPy cosine similarity and FAISS (`faiss.IndexFlatIP`).
- `reranker.py`: Candidate aggregation across multiple photos of consenting subjects (using max-pooling over embeddings or highest candidate similarity to prevent bias towards users with more photos).

### 3. Gallery & Ingestion (`backend/app/database/`, `backend/scripts/`)
- SQLite database via SQLAlchemy with migration-ready abstractions.
- Manifest-driven gallery ingestion (`manifest.json`): enforces license, consent status, attribution, and model versioning.
- Precomputed embeddings stored in `.npy` and indexed in memory; avoids redundant inference per query.

### 4. Privacy & Security (`backend/app/core/security.py`)
- Immediate session cleanup: User selfie is stored in a temporary UUID-scoped path and deleted right after inference.
- Client-side card rendering for social sharing (zero backend exposure of raw private photos).
- No biometric vectors logged or leaked in error stack traces.
