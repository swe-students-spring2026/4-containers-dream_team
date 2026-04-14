"""
Tests for API routes.

This module verifies that core endpoints respond with expected
HTTP status codes.
"""


def test_dashboard(client):
    """Test that the dashboard endpoint returns HTTP 200."""
    res = client.get("/")
    assert res.status_code == 200


def test_post_analysis(client):
    """Test that posting analysis data returns HTTP 201."""
    res = client.post(
        "/api/analysis",
        json={"input": "x", "result": "y"},
    )
    assert res.status_code == 201


def test_get_analysis(client):
    """Test that retrieving analysis data returns HTTP 200."""
    res = client.get("/api/analysis")
    assert res.status_code == 200
