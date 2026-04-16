"""
Pytest fixtures for exercising the real Flask application.
"""

from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app as flask_app  


@pytest.fixture(name="app")
def app_fixture():
    """
    Provide the web app configured for tests.
    """

    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    """
    Provide a Flask test client for route-level tests.
    """

    return app.test_client()
