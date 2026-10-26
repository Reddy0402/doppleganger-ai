import base64
import os

import cv2
import numpy as np
import pytest

from app.core.config import settings
from app.retrieval import vector_index as vi
from app.retrieval.vector_index import GalleryRecord, VectorIndex
from app.services import match_service
from app.services.match_service import process_match_request
from app.vision.adapter import vision_adapter
from app.retrieval.vector_index import gallery_index


def _record(i: int, dim: int = 8, participant_prefix: str = "p") -> GalleryRecord:
    rng = np.random.default_rng(i)
    emb = rng.standard_normal(dim).astype(np.float32)
    emb /= np.linalg.norm(emb)
    return GalleryRecord(
        image_id=f"img_{i}",
        participant_id=f"{participant_prefix}_{i}",
        display_name=f"Person {i}",
        bio_caption="",
        image_url=f"/api/gallery/images/test_{i}.jpg",
        embedding=emb,
        subfeatures={},
    )


def _brute_force_ranking(query: np.ndarray, records):
    """Reference ranking: cosine similarity per record, descending, ties by participant."""
    q = query / np.linalg.norm(query)
    scored = [(r.image_id, float(np.dot(r.embedding, q))) for r in records]
    return sorted(scored, key=lambda x: -x[1])


# --- Test A: candidate mapping -------------------------------------------------

def test_candidate_ids_resolve_to_their_own_image():
    index = VectorIndex(dimension=8, use_faiss=False)
    records = [_record(i) for i in range(6)]
    index.add_records(records)
    by_id = {r.image_id: r for r in records}

    out = index.search(query_vec=records[2].embedding, top_k=6)

    assert out["matches"][0]["image_id"] == "img_2"
    for m in out["matches"]:
        assert m["image_url"] == by_id[m["image_id"]].image_url
        assert m["participant_id"] == by_id[m["image_id"]].participant_id


def test_duplicate_image_id_is_rejected():
    index = VectorIndex(dimension=8, use_faiss=False)
    index.add_records([_record(1)])
    with pytest.raises(ValueError, match="Duplicate gallery image_id"):
        index.add_records([_record(1)])


# --- Test C: ranking -----------------------------------------------------------

def test_ranking_is_descending_and_matches_brute_force():
    index = VectorIndex(dimension=8, use_faiss=False)
    records = [_record(i) for i in range(25)]
    index.add_records(records)
    query = np.random.default_rng(999).standard_normal(8).astype(np.float32)

    out = index.search(query_vec=query, top_k=25, mode="exact_numpy")
    scores = [m["similarity_score"] for m in out["matches"]]
    expected = _brute_force_ranking(query, records)

    assert scores == sorted(scores, reverse=True)
    assert [m["image_id"] for m in out["matches"]] == [img for img, _ in expected]
    assert [m["rank"] for m in out["matches"]] == list(range(1, 26))


@pytest.mark.skipif(not vi.HAS_FAISS, reason="faiss not installed")
def test_faiss_and_numpy_return_same_ranking():
    index = VectorIndex(dimension=8, use_faiss=True)
    index.add_records([_record(i) for i in range(30)])
    query = np.random.default_rng(7).standard_normal(8).astype(np.float32)

    numpy_ids = [m["image_id"] for m in index.search(query, top_k=30, mode="exact_numpy")["matches"]]
    faiss_ids = [m["image_id"] for m in index.search(query, top_k=30, mode="faiss")["matches"]]
    assert numpy_ids == faiss_ids


# --- Empty gallery -------------------------------------------------------------

def test_empty_index_returns_no_matches():
    index = VectorIndex(dimension=8, use_faiss=False)
    out = index.search(query_vec=np.ones(8, dtype=np.float32), top_k=5)
    assert out["matches"] == []
    assert out["total_portraits_indexed"] == 0


# --- Real gallery pipeline (uses the indexed demo gallery) ---------------------

def _gallery_image_bytes(record, quality_shift: int = 0) -> bytes:
    path = os.path.join(settings.GALLERY_DIR, "images", os.path.basename(record.image_url))
    img = cv2.imread(path)
    assert img is not None, f"gallery image missing: {path}"
    if quality_shift:
        img = cv2.convertScaleAbs(img, alpha=1.0, beta=quality_shift)
    ok, buf = cv2.imencode(".jpg", img)
    assert ok
    return buf.tobytes()


def _pick_records(n: int = 3):
    recs = gallery_index.records
    assert len(recs) >= 1000, "gallery must be indexed (run backend/scripts/ingest_gallery.py)"
    step = len(recs) // (n + 1)
    return [recs[(i + 1) * step] for i in range(n)]


def test_different_queries_are_ranked_independently():
    queries = _pick_records(3)
    top_ids = []
    for rec in queries:
        file_bytes = _gallery_image_bytes(rec)
        resp = process_match_request(file_bytes, top_k=10)
        assert resp["status"] == "SUCCESS"

        # Reference: compute this query's own embedding and rank the full gallery
        proc = vision_adapter.process_image(cv2.cvtColor(
            cv2.imdecode(np.frombuffer(file_bytes, np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB))
        expected = _brute_force_ranking(proc["embedding"], gallery_index.records)
        expected_top = [img for img, _ in expected[:10]]

        returned = [m["image_id"] for m in resp["matches"]]
        assert returned[0] == rec.image_id  # the query is itself in the gallery
        assert returned == expected_top[:len(returned)]
        top_ids.append(returned[0])

    assert len(set(top_ids)) == len(top_ids), "different queries must not collapse to one match"


def test_repeated_query_gives_consistent_results():
    rec = _pick_records(1)[0]
    file_bytes = _gallery_image_bytes(rec, quality_shift=12)
    first = process_match_request(file_bytes, top_k=10)
    second = process_match_request(file_bytes, top_k=10)

    assert [m["image_id"] for m in first["matches"]] == [m["image_id"] for m in second["matches"]]
    assert [m["similarity_score"] for m in first["matches"]] == [m["similarity_score"] for m in second["matches"]]


def test_each_match_image_url_belongs_to_its_candidate():
    rec = _pick_records(1)[0]
    resp = process_match_request(_gallery_image_bytes(rec), top_k=10)
    by_id = {r.image_id: r for r in gallery_index.records}
    for m in resp["matches"]:
        assert m["image_url"] == by_id[m["image_id"]].image_url
        assert os.path.exists(os.path.join(settings.GALLERY_DIR, "images", os.path.basename(m["image_url"])))


def test_upload_sequence_second_query_is_not_stale():
    """A file upload followed by a base64 (camera-style) query must search the second image."""
    a, b = _pick_records(2)
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as client:
        r1 = client.post("/api/matches", files={"file": ("a.jpg", _gallery_image_bytes(a), "image/jpeg")},
                         data={"top_k": "5"}).json()
        b64 = base64.b64encode(_gallery_image_bytes(b)).decode()
        r2 = client.post("/api/matches", data={"image_base64": f"data:image/jpeg;base64,{b64}", "top_k": "5"}).json()

    assert r1["matches"][0]["image_id"] == a.image_id
    assert r2["matches"][0]["image_id"] == b.image_id


# --- Failure handling ----------------------------------------------------------

def test_blank_image_reports_no_face():
    blank = np.full((300, 300, 3), 200, dtype=np.uint8)
    ok, buf = cv2.imencode(".jpg", blank)
    resp = process_match_request(buf.tobytes(), top_k=5)
    assert resp["status"] == "NO_FACE_DETECTED"
    assert resp["matches"] == []


def test_invalid_bytes_are_rejected():
    resp = process_match_request(b"not an image at all", top_k=5)
    assert resp["status"] == "INVALID_IMAGE"
    assert resp["matches"] == []


def test_non_finite_embedding_is_rejected(monkeypatch):
    original = vision_adapter.process_image

    def fake_process(image_rgb, selected_face_index=None):
        result = original(image_rgb, selected_face_index=selected_face_index)
        if result["status"] == "SUCCESS":
            result["embedding"] = np.full_like(result["embedding"], np.nan)
        return result

    monkeypatch.setattr(vision_adapter, "process_image", fake_process)
    rec = _pick_records(1)[0]
    resp = process_match_request(_gallery_image_bytes(rec), top_k=5)
    assert resp["status"] == "PROCESSING_ERROR"
    assert resp["matches"] == []


def test_query_from_different_model_is_refused(monkeypatch):
    """Vectors from different models are not comparable; the search must not run."""
    rec = _pick_records(1)[0]
    monkeypatch.setattr(gallery_index, "model_name", "some_other_model")
    resp = process_match_request(_gallery_image_bytes(rec), top_k=5)
    assert resp["status"] == "MODEL_MISMATCH"
    assert resp["matches"] == []
