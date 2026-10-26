# Model Selection, Licensing, and Benchmark Rationale

## Selected Face Detection and Recognition Architecture

### 1. Face Detector: OpenCV YuNet (Apache 2.0)
- **Architecture**: Lightweight single-stage CNN face detector optimized for edge and CPU inference.
- **Output**: Bounding box `[x, y, w, h]`, confidence score, and 5 facial landmarks:
  1. Right eye center
  2. Left eye center
  3. Nose tip
  4. Right corner of mouth
  5. Left corner of mouth
- **License**: Apache 2.0 (OpenCV Zoo). Free for commercial and non-commercial deployment.
- **Why Chosen**: Extremely fast CPU inference (<15ms per frame on modern x86_64 CPUs), zero complex C++ wheel compilation issues on Windows, natively supported by OpenCV 4.x / 5.x `FaceDetectorYN`.

### 2. Face Embedding Model: SFace / ArcFace (Apache 2.0 / MIT)
- **Architecture**: ResNet-style deep feature extractor trained with ArcFace (Additive Angular Margin Loss).
- **Embedding Dimension**: 128-dimensional (SFace) / 512-dimensional (ArcFace ONNX) L2-normalized feature representation.
- **Preprocessing Alignment**: Standard 5-point similarity transformation mapping eye pupils to canonical positions `(0.35, 0.35)` and `(0.65, 0.35)` in a 112x112 pixel crop.
- **Metric**: Cosine Similarity:
  $$\text{sim}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$$
  Because embeddings are unit-normalized ($||u||_2 = 1.0$), cosine similarity simplifies to the Euclidean dot product:
  $$\text{sim}(u, v) = u \cdot v$$
- **License**: Apache 2.0 (SFace by OpenCV Zoo) and MIT (ArcFace ONNX). Clean, unencumbered license without restrictive non-commercial research-only clauses.

### 3. Comparison with Alternative Models
- **AdaFace**: Excellent for low-quality faces (adaptive margin based on image quality). However, official PyTorch checkpoints require PyTorch + torchvision with complex dependencies.
- **CLIP (ViT-B/32)**: Strong for semantic text-image and broad categorization, but poor at fine-grained facial identity and landmark-guided geometric alignment. Included as an exploratory baseline to demonstrate why specialized face-metric models outperform generalized vision-language models for lookalike retrieval.

## Resemblance vs. Verification
Standard face recognition optimizes for **verification** (threshold $\approx 0.65+$ where false acceptance rate is $< 10^{-4}$). In contrast, **lookalike retrieval** operates in the mid-similarity band (typically $0.35 - 0.60$ for distinct individuals who exhibit remarkable visual resemblance in jawline, eye spacing, nose bridge, or facial symmetry).
The application maps cosine similarities to intuitive calibrated percentage tiers while explicitly maintaining that high visual similarity does not imply biological kinship or identity.
