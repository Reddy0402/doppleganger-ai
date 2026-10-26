# Doppelgänger AI: Setup and Operations Manual

## Prerequisites
- Node.js >= 18 (Tested on v24)
- Python 3.10, 3.11, or 3.12 (Tested on 3.11.9)
- Modern Web Browser (Chrome, Firefox, Safari, Edge with WebCam support)

## Quick Start (Clean Checkout)

### 1. Backend Setup
From the repository root:
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
# or: source .venv/bin/activate  # macOS / Linux

# Install dependencies
pip install -r backend/requirements.txt

# Download model checkpoints (YuNet & SFace) and bootstrap demo gallery
python backend/scripts/download_models.py
python backend/scripts/ingest_gallery.py

# Launch FastAPI server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

The API docs will be available at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
From the repository root:
```bash
cd frontend
npm install
npm run dev
```

The web application will be live at: `http://localhost:5173`

### 3. Ingesting External Datasets (CelebAMask-HQ, CelebA-Spoof, InsightFace)
To expand your searchable gallery beyond the default demo participants with external datasets:

```bash
# Ingest CelebAMask-HQ or CelebA-Spoof portraits:
python backend/scripts/ingest_external_dataset.py --source "path/to/celeba_images" --dataset "CelebAMask-HQ" --limit 1000

# Ingest InsightFace aligned crops:
python backend/scripts/ingest_external_dataset.py --source "path/to/insightface_crops" --dataset "InsightFace" --limit 1000
```
This automatically runs YuNet face detection, canonical 5-point alignment, quality scoring, extracts 128D SFace/ArcFace embeddings, and updates the FAISS vector index.

### 4. Running Automated Tests & Benchmark
```bash
# Run backend unit & integration tests
pytest backend/tests/ -v

# Run reproducible evaluation benchmark
python backend/scripts/evaluate_retrieval.py
```
Outputs will be produced in `data/evaluation/`:
- `metrics.json`
- `model_comparison.csv`
- `evaluation_report.md`

