from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ModelMetrics(BaseModel):
    model_name: str
    detector: str
    dimension: int
    precision_at_1: float
    precision_at_5: float
    recall_at_5: float
    mean_average_precision: float
    ndcg_at_5: float
    mean_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    ranking_stability: float
    failure_rate: float
    evaluated_queries_count: int

class EvaluationSummaryResponse(BaseModel):
    timestamp: str
    benchmark_metadata: Dict[str, Any]
    models: Dict[str, ModelMetrics]
