"""
Pytest configuration and fixtures for testing the Flask application.
This module provides a test client for making requests to the app
without running the actual server.
"""

import pytest
from app import create_app

@pytest.fixture
def app():
    """
    Create and configure a new Flask app instance for testing.

    This ensures each test runs with a fresh application context.
    """
    app = create_app()

    # @TODO configure test settings here (e.g. testing database)
    app.config["TESTING"] = True

    return app

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

