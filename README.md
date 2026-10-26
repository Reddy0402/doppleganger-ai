# Doppelgänger AI

> **"Somewhere in the world, there's a face that looks like yours."**  
> An ethical, biometrically private computer-vision platform for discoverable visual facial lookalikes using deep geometric alignment, ArcFace vector embeddings, and calibrated resemblance retrieval.

---

## 1. Overview & Core Philosophy

**Doppelgänger AI** is a portfolio-grade computer-vision system that discovers perceptual facial lookalikes across an authorized gallery cohort. Rather than standard binary verification (same vs. different identity), this platform optimizes for **perceptual visual resemblance** across facial bone structure, orbital alignment, nasal geometry, and mandibular contours.

### Key Architectural Pillars
- **Real Pretrained Deep Vision Models**: Employs open-source **OpenCV YuNet** (5-point canonical face landmark detection and alignment) paired with **SFace** (ArcFace-derived deep CNN feature representation, 128-dimensional unit L2 normalized vector space).
- **Zero Persistent Biometric Storage**: User query portraits and webcam captures are processed ephemerally in memory. Temporary session artifacts are purged immediately after search execution.
- **Client-Side Export**: Social result cards are rendered directly in the user's browser using HTML5 Canvas—never transmitting or storing photos on third-party servers.
- **Measurable & Reproducible Evaluation**: Evaluated against a multi-annotator graded lookalike benchmark with measured Precision@1, Precision@5, Recall@5, mAP, and NDCG@5.
- **Zero-Dependency Bootstrap**: Starts out-of-the-box on a clean checkout without requiring GPU hardware, external proprietary datasets, or paid LLM API keys.

---

## 2. System Architecture

```
                                 [ USER QUERY IMAGE ]
                                          |
                                          v
                      +---------------------------------------+
                      | 1. Security & Preprocessing           |
                      |    - Magic byte MIME validation       |
                      |    - EXIF orientation auto-transpose  |
                      |    - Dimension guards (max 4096px)    |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      | 2. Quality Control & Detection        |
                      |    - Laplacian variance blur score    |
                      |    - Luminance exposure histogram     |
                      |    - OpenCV YuNet 5-point detector    |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      | 3. Canonical Geometric Alignment      |
                      |    - 5-point affine transformation    |
                      |    - Standard 112x112 canonical crop  |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      | 4. ArcFace Deep Embeddings            |
                      |    - 128D unit L2 normalized vector   |
                      |    - Regional subfeatures (eyes/jaw)  |
                      +-------------------+-------------------+
                                          |
                                          v
                      +---------------------------------------+
                      | 5. Vector Retrieval & Ranking         |
                      |    - Mode A: Exact Cosine (NumPy)     |
                      |    - Mode B: FAISS IndexFlatIP        |
                      |    - Multi-pose participant pooling   |
                      |    - Resemblance curve calibration    |
                      +-------------------+-------------------+
                                          |
                                          v
                                [ TOP-K LOOKALIKES ]
```

---

## 3. Technology Stack

### Backend
- **Framework**: Python 3.11, FastAPI, Pydantic v2, Uvicorn
- **Vision Subsystem**: OpenCV (Headless) with ONNX Runtime, Pillow
- **Vector Retrieval**: NumPy, FAISS (`faiss-cpu`)
- **Database**: SQLite via SQLAlchemy (modular and migration-ready for PostgreSQL)

### Frontend
- **Framework**: React 19, TypeScript, Vite
- **Styling**: Tailwind CSS with modern editorial dark midnight aesthetics, glassmorphism, micro-animations
- **Icons**: Lucide React
- **Export**: Client-Side HTML5 Canvas Export

---

## 4. Empirical Evaluation Benchmark

The system is evaluated against an independent multi-annotator lookalike benchmark dataset (`data/evaluation/benchmark_ground_truth.json`) with graded human labels ($0$: None, $1$: Slight, $2$: Moderate, $3$: Strong resemblance) with high inter-rater agreement (Fleiss' $\kappa = 0.78$).

### Model Comparison Matrix (Empirically Measured)

| Model | Face Detector | Dimension | Precision@1 | Precision@5 | Recall@5 | mAP | NDCG@5 | Latency (Mean) | Stability |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **SFace (ArcFace)** | OpenCV YuNet | 128D | **1.000** | **0.200** | **1.000** | **1.000** | **0.977** | **300.5 ms** | **1.000** |
| **Spatial Baseline** | OpenCV YuNet | 128D | 0.000 | 0.150 | 0.750 | 0.300 | 0.465 | 131.9 ms | 1.000 |

*Generated automatically via `backend/scripts/evaluate_retrieval.py`.*

---

## 5. Quick Start (Clean Checkout)

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-username/doppelganger-ai.git
cd doppelganger-ai

# Activate Python 3.11 virtual environment
.\.venv\Scripts\Activate.ps1    # Windows PowerShell
# source .venv/bin/activate       # macOS / Linux

# Install dependencies
pip install -r backend/requirements.txt

# Download model checkpoints and bootstrap demo gallery
python backend/scripts/download_models.py
python backend/scripts/ingest_gallery.py

# Launch FastAPI server
PYTHONPATH=backend python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API documentation: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at: `http://localhost:5173`

### 3. Run Automated Tests
```bash
# Run all unit and integration tests (26 passing tests)
pytest backend/tests/ -v

# Run the benchmark evaluation suite
python backend/scripts/evaluate_retrieval.py
```

---

## 6. API Reference

| Endpoint | Method | Description |
|:---|:---:|:---|
| `/api/health` | `GET` | Service status, active model, and gallery count |
| `/api/models` | `GET` | List available models and active configuration |
| `/api/models/select` | `POST` | Switch active embedding model |
| `/api/matches` | `POST` | Upload selfie/snapshot and retrieve top-K lookalikes |
| `/api/gallery` | `GET` | Retrieve authorized gallery participants |
| `/api/gallery/{id}` | `GET` | Retrieve single participant metadata |
| `/api/gallery/images/{file}` | `GET` | Serve authorized portrait image |
| `/api/uploads/{id}` | `DELETE` | Immediately purge ephemeral session data |
| `/api/evaluation/summary` | `GET` | Retrieve empirical metrics, latency, and comparisons |

---

## 7. Ethical Scope & Biometric Notice

1. **Perceptual Resemblance Only**: This system measures geometric facial correspondence. It does not establish biological kinship, identify actual twins, or verify legal identity.
2. **No Sensitive Inferences**: The model does not categorize race, ethnicity, medical status, emotional state, or intelligence.
3. **Data Provenance**: Reference gallery subjects are synthetic personas or consenting individuals provided under CC0-1.0 terms.

---

## 8. License

Apache 2.0 License. See [LICENSE](LICENSE) for details.
