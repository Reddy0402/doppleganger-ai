import os
import io
import base64
import pytest
from PIL import Image

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "Doppelgänger AI API"
    assert data["gallery_portraits_count"] >= 1

def test_models_endpoint(client):
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "available_models" in data
    assert len(data["available_models"]) >= 2
    assert data["active_model"] in ["sface", "deterministic"]

def test_gallery_endpoints(client):
    response = client.get("/api/gallery")
    assert response.status_code == 200
    data = response.json()
    assert data["total_participants"] >= 1
    assert len(data["participants"]) >= 1

    first_p = data["participants"][0]
    p_id = first_p["id"]
    
    # Get specific participant
    p_resp = client.get(f"/api/gallery/{p_id}")
    assert p_resp.status_code == 200
    p_data = p_resp.json()
    assert p_data["id"] == p_id
    assert p_data["display_name"] == first_p["display_name"]

def test_gallery_image_serve(client):
    response = client.get("/api/gallery/images/portrait_elena_1.jpg")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")

def test_evaluation_summary_endpoint(client):
    response = client.get("/api/evaluation/summary")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "sface" in data["models"]

def test_delete_upload_endpoint(client):
    response = client.delete("/api/uploads/non-existent-test-id")
    assert response.status_code == 200
    assert response.json()["status"] in ["success", "not_found"]

def test_gallery_stats_endpoint(client):
    response = client.get("/api/gallery/stats")
    assert response.status_code == 200
    data = response.json()
    assert "unique_participants" in data
    assert "indexed_portraits" in data
    assert data["unique_participants"] >= 1
    assert data["indexed_portraits"] >= data["unique_participants"]

def test_gallery_reindex_endpoint(client):
    response = client.post("/api/gallery/reindex")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["unique_participants"] >= 1

def test_match_endpoint_with_real_portrait(client):
    # Use real test portrait
    portrait_path = os.path.join("data", "demo_gallery", "images", "portrait_elena_1.jpg")
    with open(portrait_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/matches",
        files={"file": ("test_elena.jpg", file_bytes, "image/jpeg")},
        data={"top_k": 5, "aggregation_policy": "max"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["num_faces_detected"] == 1
    assert len(data["matches"]) >= 1
    assert "stats" in data
    assert data["stats"]["total_qualifying"] >= 1
    assert data["stats"]["total_participants_searched"] >= 1
    
    top_match = data["matches"][0]
    # Elena's query against the gallery must find Elena Vance as #1 match
    assert top_match["participant_id"] == "p_elena"
    assert top_match["resemblance_percentage"] >= 80.0
    assert top_match["rank"] == 1
    assert "fun_caption" in top_match
    assert "subfeature_breakdown" in top_match

def test_match_endpoint_camera_base64_parity(client):
    """Verifies that live camera base64 data undergoes the exact same retrieval pipeline and results."""
    portrait_path = os.path.join("data", "demo_gallery", "images", "portrait_elena_1.jpg")
    with open(portrait_path, "rb") as f:
        b64_str = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

    response = client.post(
        "/api/matches",
        data={"image_base64": b64_str, "top_k": 5, "min_threshold": 50.0}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["matches"][0]["participant_id"] == "p_elena"
    assert data["stats"]["resemblance_threshold"] == 50.0

def test_match_endpoint_threshold_zero_matches(client):
    """Setting threshold to 99.9% should return 0 qualifying matches without crashing."""
    portrait_path = os.path.join("data", "demo_gallery", "images", "portrait_elena_1.jpg")
    with open(portrait_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/matches",
        files={"file": ("test_elena.jpg", file_bytes, "image/jpeg")},
        data={"top_k": 5, "min_threshold": 99.9}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["matches"]) == 0
    assert data["stats"]["total_qualifying"] == 0

def test_match_endpoint_with_no_face_image(client):
    # Create plain solid blue image with no faces
    img = Image.new("RGB", (200, 200), color=(10, 20, 150))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    
    response = client.post(
        "/api/matches",
        files={"file": ("blank.jpg", buf.getvalue(), "image/jpeg")},
        data={"top_k": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NO_FACE_DETECTED"
    assert data["matches"] == []

