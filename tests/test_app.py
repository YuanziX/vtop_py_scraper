"""Basic tests for the VTOP scraper API."""

import pytest
from fastapi.testclient import TestClient

from vtop_scraper.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint returns the expected message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "VTOP-AP API"}


def test_verify_endpoint_missing_credentials(client):
    """Test verify endpoint with missing credentials."""
    response = client.post("/api/verify", data={})
    assert response.status_code == 422


def test_attendance_endpoint_missing_credentials(client):
    """Test attendance endpoint with missing credentials."""
    response = client.post("/api/attendance", data={})
    assert response.status_code == 422
