import pytest
from app.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    average_precision,
    mean_average_precision,
    dcg_at_k,
    ndcg_at_k,
    topk_jaccard_stability
)

def test_precision_at_k():
    # Graded labels: [3, 2, 1, 0, 2] (threshold=2)
    # Ranks 1, 2, 5 meet threshold
    labels = [3, 2, 1, 0, 2]
    assert precision_at_k(labels, k=1, threshold=2) == 1.0  # [3] -> 1/1
    assert precision_at_k(labels, k=2, threshold=2) == 1.0  # [3, 2] -> 2/2
    assert precision_at_k(labels, k=3, threshold=2) == round(2/3, 4) # [3, 2, 1] -> 2/3
    assert precision_at_k(labels, k=5, threshold=2) == 0.6  # [3, 2, 1, 0, 2] -> 3/5

def test_recall_at_k():
    labels = [3, 2, 1, 0, 2]  # Total relevant = 3
    assert recall_at_k(labels, total_relevant=3, k=2, threshold=2) == round(2/3, 4)
    assert recall_at_k(labels, total_relevant=3, k=5, threshold=2) == 1.0

def test_ndcg_at_k_perfect_ranking():
    # If ranked order is already sorted descending [3, 2, 1, 0], NDCG must be 1.0
    labels = [3, 2, 1, 0]
    ideal = [3, 2, 1, 0]
    assert ndcg_at_k(labels, ideal, k=4) == 1.0

def test_ndcg_at_k_inverted_ranking():
    # If relevant items are buried at bottom, NDCG should be significantly lower
    worst = [0, 0, 1, 3]
    ideal = [3, 1, 0, 0]
    score = ndcg_at_k(worst, ideal, k=4)
    assert 0.0 < score < 0.6

def test_topk_jaccard_stability():
    rank_a = ["p1", "p2", "p3", "p4", "p5"]
    rank_b = ["p1", "p2", "p3", "p5", "p6"]
    # Intersection = {p1, p2, p3, p5} (4), Union = 6 -> Jaccard = 4/6 = 0.6667
    assert topk_jaccard_stability(rank_a, rank_b, k=5) == round(4/6, 4)
    assert topk_jaccard_stability(rank_a, rank_a, k=5) == 1.0
