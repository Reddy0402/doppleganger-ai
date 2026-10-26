import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.retrieval.similarity import (
    batch_cosine_similarity,
    calibrate_resemblance_score,
    compute_subfeature_breakdown
)

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

class GalleryRecord:
    def __init__(
        self,
        image_id: str,
        participant_id: str,
        display_name: str,
        bio_caption: str,
        image_url: str,
        embedding: np.ndarray,
        subfeatures: Dict[str, np.ndarray],
        quality_score: float = 1.0,
        license_info: str = "CC0-1.0",
        consent_status: str = "synthetic_authorized"
    ):
        self.image_id = image_id
        self.participant_id = participant_id
        self.display_name = display_name
        self.bio_caption = bio_caption
        self.image_url = image_url
        self.embedding = embedding
        self.subfeatures = subfeatures
        self.quality_score = quality_score
        self.license_info = license_info
        self.consent_status = consent_status

class VectorIndex:
    def __init__(self, dimension: int = 128, use_faiss: bool = True):
        self.dimension = dimension
        self.use_faiss = use_faiss and HAS_FAISS
        self.records: List[GalleryRecord] = []
        self.matrix: Optional[np.ndarray] = None
        self.faiss_index = None

    def clear(self):
        self.records = []
        self.matrix = None
        self.faiss_index = None

    def add_records(self, records: List[GalleryRecord]):
        for r in records:
            if r.embedding.shape[0] != self.dimension:
                raise ValueError(
                    f"Vector dimension mismatch: expected {self.dimension}, got {r.embedding.shape[0]}"
                )
            self.records.append(r)
        self.rebuild_index()

    def rebuild_index(self):
        if len(self.records) == 0:
            self.matrix = None
            self.faiss_index = None
            return

        # Stack into 2D matrix (N, D)
        embeddings = [r.embedding for r in self.records]
        self.matrix = np.vstack(embeddings).astype(np.float32)

        if self.use_faiss and HAS_FAISS:
            # IndexFlatIP does exact inner product search on L2-normalized vectors (exact cosine)
            self.faiss_index = faiss.IndexFlatIP(self.dimension)
            self.faiss_index.add(self.matrix)

    def search(
        self,
        query_vec: np.ndarray,
        query_subfeatures: Optional[Dict[str, np.ndarray]] = None,
        top_k: Optional[int] = None,
        min_threshold: float = 0.0,
        aggregation_policy: str = "max",  # "max" or "average"
        mode: str = "auto"                # "exact_numpy", "faiss", "auto"
    ) -> Dict[str, Any]:
        """
        Search complete authorized gallery for all matching participants.
        Compares query against EVERY valid portrait in the gallery.
        Aggregates multiple reference photos per unique participant using `aggregation_policy`.
        Returns all qualifying participants above `min_threshold`, ranked descending.
        """
        if len(self.records) == 0 or self.matrix is None:
            return {
                "matches": [],
                "total_qualifying": 0,
                "total_participants_searched": 0,
                "total_portraits_indexed": 0,
                "tier_counts": {
                    "exceptional": 0,
                    "strong": 0,
                    "moderate": 0,
                    "subtle": 0
                }
            }

        if query_vec.shape[0] != self.dimension:
            raise ValueError(
                f"Query dimension {query_vec.shape[0]} does not match index dimension {self.dimension}"
            )

        query_normalized = query_vec.astype(np.float32)
        norm = np.linalg.norm(query_normalized)
        if norm > 1e-12:
            query_normalized = query_normalized / norm

        # Compute raw similarity scores across ALL gallery images
        # We ensure complete coverage by querying across all records
        use_faiss_now = (mode == "faiss") or (mode == "auto" and self.use_faiss and self.faiss_index is not None)
        
        if use_faiss_now and self.faiss_index is not None:
            # Query the complete index: k = len(self.records) guarantees NO truncation of candidates
            scores, indices = self.faiss_index.search(
                np.expand_dims(query_normalized, axis=0),
                len(self.records)
            )
            image_scores = [(self.records[idx], float(sc)) for idx, sc in zip(indices[0], scores[0]) if idx != -1]
        else:
            # NumPy exact cosine baseline across the complete matrix
            sims = batch_cosine_similarity(query_normalized, self.matrix)
            image_scores = [(self.records[i], float(sims[i])) for i in range(len(self.records))]

        # Aggregate by participant
        participant_groups: Dict[str, List[tuple]] = {}
        for record, score in image_scores:
            participant_groups.setdefault(record.participant_id, []).append((record, score))

        total_participants_searched = len(participant_groups)
        total_portraits_indexed = len(self.records)

        aggregated_results = []
        tier_counts = {
            "exceptional": 0,
            "strong": 0,
            "moderate": 0,
            "subtle": 0
        }

        for p_id, items in participant_groups.items():
            scores = [sc for _, sc in items]
            if aggregation_policy == "max":
                best_record, best_score = max(items, key=lambda x: x[1])
            else:  # "average"
                best_score = float(np.mean(scores))
                best_record = max(items, key=lambda x: x[1])[0]

            calib = calibrate_resemblance_score(best_score)
            sim_score = round(best_score, 4)

            # Categorize tier count
            if calib["percentage"] >= 82.0:
                tier_counts["exceptional"] += 1
            elif calib["percentage"] >= 65.0:
                tier_counts["strong"] += 1
            elif calib["percentage"] >= 45.0:
                tier_counts["moderate"] += 1
            else:
                tier_counts["subtle"] += 1

            # Check configurable resemblance threshold (by percentage or raw cosine)
            # min_threshold is passed as resemblance percentage (0 to 100)
            if calib["percentage"] < min_threshold:
                continue

            # Sub-feature region breakdown
            breakdown = None
            if query_subfeatures is not None:
                breakdown = compute_subfeature_breakdown(query_subfeatures, best_record.subfeatures)

            aggregated_results.append({
                "participant_id": p_id,
                "display_name": best_record.display_name,
                "bio_caption": best_record.bio_caption,
                "image_id": best_record.image_id,
                "image_url": best_record.image_url,
                "quality_score": best_record.quality_score,
                "license_info": best_record.license_info,
                "consent_status": best_record.consent_status,
                "similarity_score": sim_score,
                "resemblance_percentage": calib["percentage"],
                "resemblance_tier": calib["tier"],
                "badge_color": calib["badge_color"],
                "description": calib["description"],
                "subfeature_breakdown": breakdown,
                "image_count": len(items)
            })

        # Deterministic sorting: sort descending by similarity score, then tiebreak by participant_id
        aggregated_results.sort(key=lambda x: (-x["similarity_score"], x["participant_id"]))

        total_qualifying = len(aggregated_results)

        # Assign ranks
        for rank, res in enumerate(aggregated_results, 1):
            res["rank"] = rank

        # Apply top_k slicing if specified
        if top_k is not None and top_k > 0:
            displayed_matches = aggregated_results[:top_k]
        else:
            displayed_matches = aggregated_results

        return {
            "matches": displayed_matches,
            "total_qualifying": total_qualifying,
            "total_participants_searched": total_participants_searched,
            "total_portraits_indexed": total_portraits_indexed,
            "tier_counts": tier_counts
        }

# Global singleton
gallery_index = VectorIndex()
