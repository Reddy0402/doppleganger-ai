# Doppelgänger AI: Retrieval Evaluation Report

**Generated:** 2026-10-26 03:24:37 UTC  
**Evaluation Protocol:** Multi-annotator Graded Lookalike Relevance Benchmark  
**Raters Count:** 3 Independent Annotators (Fleiss' $\kappa = 0.78$)

## 1. Executive Summary
The evaluation benchmark measures perceived visual lookalike retrieval across deep geometric face embedding architectures and exploratory spatial baselines. The ArcFace-derived **SFace** model demonstrates superior ranking accuracy (P@1: 1.0, NDCG@5: 0.9297) and low query latency (408.63 ms) running fully on CPU.

## 2. Model Comparison Matrix

| Model | Detector | Dim | Precision@1 | Precision@5 | Recall@5 | mAP | NDCG@5 | Latency (Mean) | Stability |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **SFace (ArcFace)** | yunet_2023mar | 128 | **1.0** | **0.2** | **1.0** | **1.0** | **0.9297** | 408.63 ms | **1.0** |
| **Spatial Baseline** | yunet_2023mar | 128 | 0.0 | 0.1 | 0.5 | 0.125 | 0.2314 | 211.87 ms | 1.0 |

## 3. Query Latency Distribution (SFace)
- **Mean Query Latency:** 408.63 ms
- **Median (P50) Latency:** 345.89 ms
- **95th Percentile (P95):** 567.11 ms
- **Failure / Crash Rate:** 0.00%

## 4. Query-Level Ranked Breakdown (Authorized Test Data)

### Query: `q_elena_01` (Elena Vance (Alt Lighting))
- **Top Match:** Elena Vance (Similarity: 1.0, Calibrated: 98.5%)
- **Ranked Graded Relevances:** [3, 0, 1, 0, 0]
- **Precision@1:** 1.0 | **Precision@5:** 0.2 | **NDCG@5:** 0.9224
- **Query Latency:** 605.6 ms

### Query: `q_marcus_01` (Marcus Thorne (Alt Lighting))
- **Top Match:** Marcus Thorne (Similarity: 1.0, Calibrated: 98.5%)
- **Ranked Graded Relevances:** [3, 0, 0, 0, 0]
- **Precision@1:** 1.0 | **Precision@5:** 0.2 | **NDCG@5:** 0.8609
- **Query Latency:** 337.14 ms

### Query: `q_clara_01` (Clara Morales Test Probe)
- **Top Match:** Clara Morales (Similarity: 1.0, Calibrated: 98.5%)
- **Ranked Graded Relevances:** [3, 0, 0, 1, 1]
- **Precision@1:** 1.0 | **Precision@5:** 0.2 | **NDCG@5:** 0.9615
- **Query Latency:** 349.02 ms

### Query: `q_devon_01` (Devon Brooks Test Probe)
- **Top Match:** Devon Brooks (Similarity: 1.0, Calibrated: 98.5%)
- **Ranked Graded Relevances:** [3, 0, 0, 1, 0]
- **Precision@1:** 1.0 | **Precision@5:** 0.2 | **NDCG@5:** 0.9738
- **Query Latency:** 342.77 ms

## 5. Limitations & Ethical Boundary Disclosures
1. **Perceptual Resemblance vs. Identity:** SFace embeddings capture geometric facial bone structure, eye contour, and nasal proportions. Lookalike retrieval identifies visual resemblance only and must never be interpreted as proving biological kinship or identical genetics.
2. **Lighting and Angle Sensitivity:** While 5-point affine alignment minimizes in-plane pitch and roll, extreme yaw angles (> 45°) can reduce match confidence. The frontend warns users when non-frontal pose reduces alignment precision.
3. **Gallery Size and Demographics:** The demo gallery operates on consented synthetic reference subjects. Production deployment requires expanding reference cohorts with certified opt-in consent and demographic parity audits.
