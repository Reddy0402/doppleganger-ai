import os
import sys
import pytest
import numpy as np
from fastapi.testclient import TestClient

# Ensure backend directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.database.db import init_db
from app.services.match_service import init_gallery_index

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    init_db()
    init_gallery_index()

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
