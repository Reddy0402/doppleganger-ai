# Evaluation Protocol and Metrics

## 1. Lookalike Relevance Framework

Evaluating facial resemblance requires distinguishing **lookalike retrieval** from **biometric verification**:
- Biometric verification evaluates binary 1:1 same-person identity (`y in {0, 1}`).
- Doppelgänger retrieval evaluates ranked perceived visual similarity among distinct identities using graded relevance labels:

| Grade | Label | Description |
|:---:|:---|:---|
| **0** | No resemblance | Completely dissimilar facial structure, features, and proportions |
| **1** | Slight resemblance | Shared broad trait (e.g., similar face oval or hairline) but readily distinguished |
| **2** | Moderate resemblance | Distinct facial feature similarity (e.g., eye shape, nose bridge, jawline) |
| **3** | Strong resemblance | Striking doppelgänger similarity (often mistaken in quick glance) |

## 2. Evaluation Metrics

For a set of $Q$ evaluation query portraits and ranked candidate list $R_q = [c_1, c_2, \dots, c_K]$ retrieved from gallery $\mathcal{G}$:

### Precision@K
Fraction of retrieved candidates in top-K with relevance $\ge 2$:
$$\text{Precision@K} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{\sum_{i=1}^K \mathbb{I}(\text{rel}(q, c_i) \ge 2)}{K}$$

### Recall@K
Fraction of all relevant gallery items for query $q$ captured in top-K:
$$\text{Recall@K} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{\sum_{i=1}^K \mathbb{I}(\text{rel}(q, c_i) \ge 2)}{\text{Total Relevant}(q)}$$

### Mean Average Precision (mAP)
Mean of average precision scores across recall cutoff points:
$$\text{AP}(q) = \frac{\sum_{k=1}^K P@k \cdot \mathbb{I}(\text{rel}(q, c_k) \ge 2)}{\text{Total Relevant}(q)}, \quad \text{mAP} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \text{AP}(q)$$

### Normalized Discounted Cumulative Gain (NDCG@K)
Evaluates graded relevance with logarithmic rank discount:
$$\text{DCG@K} = \sum_{i=1}^K \frac{2^{\text{rel}(q, c_i)} - 1}{\log_2(i + 1)}, \quad \text{NDCG@K} = \frac{\text{DCG@K}}{\text{IDCG@K}}$$

### Latency and Reliability Metrics
- **Mean Query Latency (ms)**: End-to-end time from image receipt to ranked JSON response.
- **Detector Failure Rate**: Percentage of valid input images where face detector failed.
- **Stability Score**: Cosine distance variation across multiple distinct photographs of the same query individual.
