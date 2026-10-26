import math
from typing import List, Dict, Any, Sequence

def precision_at_k(ranked_relevances: Sequence[int], k: int, threshold: int = 2) -> float:
    """
    Fraction of top-k retrieved items that meet or exceed relevance threshold.
    Default threshold=2 (moderate to strong resemblance).
    """
    if k <= 0:
        return 0.0
    cutoff = ranked_relevances[:k]
    if not cutoff:
        return 0.0
    relevant_count = sum(1 for r in cutoff if r >= threshold)
    return round(relevant_count / k, 4)

def recall_at_k(ranked_relevances: Sequence[int], total_relevant: int, k: int, threshold: int = 2) -> float:
    """
    Fraction of all relevant items in the gallery retrieved within top-k.
    """
    if total_relevant <= 0:
        return 1.0  # If no relevant items exist, vacuously 1.0
    cutoff = ranked_relevances[:k]
    relevant_retrieved = sum(1 for r in cutoff if r >= threshold)
    return round(relevant_retrieved / total_relevant, 4)

def average_precision(ranked_relevances: Sequence[int], total_relevant: int, k_max: int = 10, threshold: int = 2) -> float:
    """
    Computes Average Precision (AP@k_max).
    """
    if total_relevant <= 0:
        return 0.0

    score = 0.0
    hits = 0
    cutoff = ranked_relevances[:k_max]
    
    for i, rel in enumerate(cutoff, 1):
        if rel >= threshold:
            hits += 1
            score += hits / i

    return round(score / min(total_relevant, k_max), 4)

def mean_average_precision(all_ranked: List[Sequence[int]], all_totals: List[int], k_max: int = 10, threshold: int = 2) -> float:
    if not all_ranked or not all_totals or len(all_ranked) != len(all_totals):
        return 0.0
    ap_sum = sum(average_precision(r, t, k_max, threshold) for r, t in zip(all_ranked, all_totals))
    return round(ap_sum / len(all_ranked), 4)

def dcg_at_k(ranked_relevances: Sequence[int], k: int) -> float:
    """
    Computes Discounted Cumulative Gain at rank k.
    Uses exponential gain 2^rel - 1 to strongly reward top lookalikes.
    """
    dcg = 0.0
    for i, rel in enumerate(ranked_relevances[:k], 1):
        gain = (2 ** rel) - 1
        discount = math.log2(i + 1)
        dcg += gain / discount
    return dcg

def ndcg_at_k(ranked_relevances: Sequence[int], ground_truth_relevances: Sequence[int], k: int) -> float:
    """
    Normalized Discounted Cumulative Gain (NDCG@k).
    Compares DCG to Ideal DCG (IDCG) obtained by perfectly sorting ground truth labels descending.
    """
    if k <= 0:
        return 0.0

    actual_dcg = dcg_at_k(ranked_relevances, k)
    ideal_sorted = sorted(ground_truth_relevances, reverse=True)
    ideal_dcg = dcg_at_k(ideal_sorted, k)

    if ideal_dcg <= 1e-12:
        return 1.0 if actual_dcg <= 1e-12 else 0.0

    return round(actual_dcg / ideal_dcg, 4)

def topk_jaccard_stability(ranking_a: List[str], ranking_b: List[str], k: int = 5) -> float:
    """
    Computes Jaccard overlap of top-k retrieved participant IDs across two different
    photographs of the same query participant.
    """
    set_a = set(ranking_a[:k])
    set_b = set(ranking_b[:k])
    union = set_a.union(set_b)
    if not union:
        return 1.0
    intersection = set_a.intersection(set_b)
    return round(len(intersection) / len(union), 4)
