import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authed_client():
    c = TestClient(app)
    unique = uuid.uuid4().hex[:8]
    res = c.post(
        "/api/v1/auth/signup",
        json={
            "email": f"test-{unique}@example.com",
            "username": f"test-{unique}",
            "password": "testpass123",
        },
    )
    assert res.status_code == 201
    return c
