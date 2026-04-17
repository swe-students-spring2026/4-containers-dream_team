"""
Pytest fixtures for exercising the real Flask application.
"""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as app_module  # pylint: disable=import-error,wrong-import-position


class FakeCursor(list):
    """
    Tiny cursor-like wrapper that supports the Mongo sort API used by the app.
    """

    def sort(self, order):
        """
        Sort records in-place using the same field ordering as Mongo.
        """

        for field, direction in reversed(order):
            super().sort(
                key=lambda item, field=field: item.get(field, 0),
                reverse=direction < 0,
            )
        return self


class FakeInsertResult:  # pylint: disable=too-few-public-methods
    """
    Minimal insert result carrying only the inserted identifier.
    """

    # The app only reads inserted_id, so this lightweight stand-in is enough.

    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class FakeCollection:
    """
    In-memory stand-in for the Mongo collection used by the Flask app.
    """

    def __init__(self):
        self._docs = []
        self._next_id = 1

    def insert_one(self, record):
        """
        Save a copy of the record and return a Mongo-like insert result.
        """

        saved = {**record, "_id": self._next_id}
        self._next_id += 1
        self._docs.append(saved)
        return FakeInsertResult(saved["_id"])

    def find(self, _filter=None, projection=None):
        """
        Return copies of the stored records, optionally honoring simple projections.
        """

        docs = []
        for record in self._docs:
            if projection:
                docs.append(
                    {
                        field: record[field]
                        for field, include in projection.items()
                        if include and field in record
                    }
                )
                continue
            docs.append(dict(record))
        return FakeCursor(docs)

    def count_documents(self, _filter):
        """
        Report the number of stored records.
        """

        return len(self._docs)


@pytest.fixture(name="fake_collection")
def fake_collection_fixture():
    """
    Provide one shared in-memory collection per test.
    """

    return FakeCollection()


@pytest.fixture(name="app")
def app_fixture(monkeypatch, fake_collection):
    """
    Provide the web app configured for tests with an in-memory collection.
    """

    app_module.app.config["TESTING"] = True
    monkeypatch.setattr(app_module, "get_collection", lambda: fake_collection)
    return app_module.app


@pytest.fixture
def client(app):
    """
    Provide a Flask test client for route-level tests.
    """

    return app.test_client()
