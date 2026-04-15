"""
Pytest configuration and fixtures for testing the Flask application.
This module provides a test client for making requests to the app
without running the actual server.
"""

import pytest
from app import create_app  # pylint: disable=import-error


@pytest.fixture
def joke_ranking_service():
    """
    Create and configure a new Flask app instance for testing.
    """
    service = create_app()
    service.config["TESTING"] = True
    return service


@pytest.fixture
def client(app):
    """
    Provide a Flask test client for making HTTP requests
    to the application during tests.

    Usage in tests:
        def test_example(client):
            response = client.get("/")
    """
    return app.test_client()
