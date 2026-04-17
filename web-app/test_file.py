"""Tests for the Flask web app."""

import io
from unittest.mock import Mock, patch

import pytest

from app import app


@pytest.fixture(name="client")
def client_fixture():
    """Create a Flask test client."""
    app.config["TESTING"] = True
    return app.test_client()


def test_dashboard(client):
    """Test that the dashboard endpoint returns HTTP 200."""
    res = client.get("/")
    assert res.status_code == 200


def test_post_analysis(client):
    """
    Ensure POST /api/analysis returns 201 when given valid audio input,
    with ML service and database interactions mocked.
    """
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "text": "funny joke",
        "classification": "funny",
        "score": 10,
    }

    fake_insert = Mock()
    fake_insert.inserted_id = "123"

    with patch("app.requests.post", return_value=fake_response), patch(
        "app.collection.insert_one", return_value=fake_insert
    ):

        res = client.post(
            "/api/analysis",
            data={
                "username": "Sam",
                "joke": (io.BytesIO(b"fake audio"), "joke.webm"),
            },
            content_type="multipart/form-data",
        )

    assert res.status_code == 201


def test_get_analysis(client):
    """Test that retrieving analysis data returns HTTP 200."""
    with patch("app.collection.find", return_value=[]):
        res = client.get("/api/analysis")
    assert res.status_code == 200


def test_post_analysis_missing_file(client):
    """Ensure POST /api/analysis returns 400 if no audio file is provided."""

    res = client.post(
        "/api/analysis",
        data={"username": "Sam"},
        content_type="multipart/form-data",
    )

    assert res.status_code == 400
    assert res.get_json()["error"] == "missing input"


def test_post_analysis_ml_failure(client):
    """Ensure POST /api/analysis returns 500 if the ML service fails."""

    fake_response = Mock()
    fake_response.status_code = 500

    with patch("app.requests.post", return_value=fake_response):

        res = client.post(
            "/api/analysis",
            data={
                "username": "Sam",
                "joke": (io.BytesIO(b"audio"), "joke.webm"),
            },
            content_type="multipart/form-data",
        )

    assert res.status_code == 500
