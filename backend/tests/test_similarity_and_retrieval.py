import pytest
import numpy as np
from backend.app.retrieval.similarity import (
    cosine_similarity,
    batch_cosine_similarity,
    calibrate_resemblance_score
)
from backend.app.retrieval.vector_index import VectorIndex, GalleryRecord
from backend.app.vision.embeddings import normalize_l2

def test_normalize_l2_unit_length():
    v = np.array([3.0, 4.0], dtype=np.float32)
    normed = normalize_l2(v)
    assert pytest.approx(np.linalg.norm(normed), rel=1e-5) == 1.0

def test_normalize_l2_zero_vector_handled():
    zero_v = np.zeros(128, dtype=np.float32)
    normed = normalize_l2(zero_v)
    assert np.all(normed == 0.0)
    assert not np.isnan(normed).any()

def test_cosine_similarity_identical_vectors():
    v = normalize_l2(np.random.randn(128).astype(np.float32))
    assert pytest.approx(cosine_similarity(v, v), abs=1e-5) == 1.0

def test_cosine_similarity_orthogonal_vectors():
    v1 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v2 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    assert pytest.approx(cosine_similarity(v1, v2), abs=1e-5) == 0.0

def test_cosine_similarity_incompatible_dimensions():
    v1 = np.ones(128, dtype=np.float32)
    v2 = np.ones(64, dtype=np.float32)
    with pytest.raises(ValueError):
        cosine_similarity(v1, v2)

def test_empty_gallery_search():
    idx = VectorIndex(dimension=128)
    query = normalize_l2(np.random.randn(128).astype(np.float32))
    results = idx.search(query, top_k=5)
    assert results["matches"] == []
    assert results["total_qualifying"] == 0
    assert results["total_participants_searched"] == 0

def test_vector_index_ranking_and_tie_breaking():
    idx = VectorIndex(dimension=4, use_faiss=False)
    # 3 participants with known vectors
    q = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    v_high = np.array([0.9, 0.1, 0.0, 0.0], dtype=np.float32)
    v_mid = np.array([0.5, 0.5, 0.0, 0.0], dtype=np.float32)
    v_low = np.array([0.1, 0.9, 0.0, 0.0], dtype=np.float32)

    records = [
        GalleryRecord("img_1", "p_low", "Low Match", "", "", normalize_l2(v_low), {}),
        GalleryRecord("img_2", "p_high", "High Match", "", "", normalize_l2(v_high), {}),
        GalleryRecord("img_3", "p_mid", "Mid Match", "", "", normalize_l2(v_mid), {}),
    ]
    idx.add_records(records)
    
    res = idx.search(q, top_k=3)
    matches = res["matches"]
    assert len(matches) == 3
    assert res["total_qualifying"] == 3
    assert res["total_participants_searched"] == 3
    assert matches[0]["participant_id"] == "p_high"
    assert matches[1]["participant_id"] == "p_mid"
    assert matches[2]["participant_id"] == "p_low"
    assert matches[0]["rank"] == 1
    assert matches[1]["rank"] == 2
    assert matches[2]["rank"] == 3

def test_multi_image_participant_aggregation():
    idx = VectorIndex(dimension=4, use_faiss=False)
    q = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    
    # Participant A has 2 images: one medium, one excellent
    # Participant B has 1 image: good
    r_a1 = GalleryRecord("img_a1", "p_a", "Alice", "", "", normalize_l2(np.array([0.4, 0.4, 0.0, 0.0], dtype=np.float32)), {})
    r_a2 = GalleryRecord("img_a2", "p_a", "Alice", "", "", normalize_l2(np.array([0.95, 0.05, 0.0, 0.0], dtype=np.float32)), {})
    r_b1 = GalleryRecord("img_b1", "p_b", "Bob", "", "", normalize_l2(np.array([0.8, 0.2, 0.0, 0.0], dtype=np.float32)), {})

    idx.add_records([r_a1, r_a2, r_b1])
    
    # With max aggregation, Alice should rank #1 because her best image (0.95) beats Bob (0.8)
    res_max = idx.search(q, top_k=2, aggregation_policy="max")
    matches_max = res_max["matches"]
    assert matches_max[0]["participant_id"] == "p_a"
    assert matches_max[1]["participant_id"] == "p_b"
    assert matches_max[0]["image_count"] == 2
    # Ensure deduplicated unique participants count is 2 (Alice & Bob), not 3 images
    assert res_max["total_participants_searched"] == 2
    assert res_max["total_portraits_indexed"] == 3

def test_resemblance_threshold_filtering_and_zero_matches():
    idx = VectorIndex(dimension=4, use_faiss=False)
    q = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    v_low = np.array([0.2, 0.8, 0.0, 0.0], dtype=np.float32)
    idx.add_records([GalleryRecord("img_1", "p_1", "Low Match", "", "", normalize_l2(v_low), {})])

    # Unfiltered search
    res_all = idx.search(q, min_threshold=0.0)
    assert len(res_all["matches"]) == 1

    # Extremely high threshold filters out match and returns 0 matches
    res_strict = idx.search(q, min_threshold=95.0)
    assert len(res_strict["matches"]) == 0
    assert res_strict["total_qualifying"] == 0
    assert res_strict["total_participants_searched"] == 1

def test_independent_threshold_and_display_limit():
    idx = VectorIndex(dimension=4, use_faiss=False)
    q = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    records = [
        GalleryRecord(f"img_{i}", f"p_{i}", f"Person {i}", "", "", normalize_l2(np.array([0.9, float(i)*0.01, 0.0, 0.0], dtype=np.float32)), {})
        for i in range(10)
    ]
    idx.add_records(records)

    # Low threshold qualifies all 10 participants, but top_k limits display to 3
    res = idx.search(q, top_k=3, min_threshold=20.0)
    assert res["total_qualifying"] == 10
    assert len(res["matches"]) == 3
    assert res["matches"][0]["rank"] == 1
    assert res["matches"][2]["rank"] == 3

