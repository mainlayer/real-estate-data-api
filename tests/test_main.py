"""Tests for the Real Estate Data API."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_mainlayer():
    access_granted = MagicMock(authorized=True)
    access_denied = MagicMock(authorized=False)

    mock_ml = MagicMock()
    mock_ml.resources.verify_access = AsyncMock(return_value=access_granted)

    with patch("src.main.ml", mock_ml):
        yield mock_ml, access_granted, access_denied


@pytest.fixture()
def client(mock_mainlayer):
    from src.main import app
    return TestClient(app)


def test_list_properties_requires_token(client):
    resp = client.get("/properties")
    assert resp.status_code == 422


def test_list_properties_with_invalid_token_returns_402(client, mock_mainlayer):
    mock_ml, _, access_denied = mock_mainlayer
    mock_ml.resources.verify_access = AsyncMock(return_value=access_denied)

    resp = client.get("/properties", headers={"X-Mainlayer-Token": "bad"})
    assert resp.status_code == 402
    assert resp.json()["detail"]["error"] == "payment_required"


def test_list_properties_success(client):
    resp = client.get("/properties", headers={"X-Mainlayer-Token": "valid"})
    assert resp.status_code == 200
    data = resp.json()
    assert "properties" in data
    assert "total_results" in data
    assert data["total_results"] > 0


def test_list_properties_filter_city(client):
    resp = client.get(
        "/properties",
        headers={"X-Mainlayer-Token": "valid"},
        params={"city": "Austin"},
    )
    assert resp.status_code == 200
    for prop in resp.json()["properties"]:
        assert "austin" in prop["city"].lower()


def test_get_property_detail(client):
    resp = client.get("/properties/atx-001", headers={"X-Mainlayer-Token": "valid"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "atx-001"


def test_get_property_not_found(client):
    resp = client.get("/properties/nonexistent-xyz", headers={"X-Mainlayer-Token": "valid"})
    assert resp.status_code == 404


def test_search_properties(client):
    resp = client.post(
        "/search",
        headers={"X-Mainlayer-Token": "valid"},
        json={"min_beds": 3, "max_price": 2_000_000},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "properties" in data
    for prop in data["properties"]:
        assert prop["bedrooms"] >= 3
        assert prop["price"] <= 2_000_000


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
