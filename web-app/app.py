"""Flask bridge for frontend joke transcription and submission."""

import os
from functools import lru_cache
from pathlib import Path
from time import time

from flask import Flask, jsonify, request, send_from_directory
from pymongo import DESCENDING, MongoClient, errors
import requests

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent

# Use Docker service names so every app instance talks to the same stack.
ML_URL = "http://machine-learning-client:5001/process"
MONGO_URI = os.getenv("MONGO_URI") or "mongodb://mongodb:27017"
SORT_ORDER = [("funniness_score", DESCENDING), ("created_at", DESCENDING)]


@lru_cache(maxsize=1)
def get_collection():
    """Connect to MongoDB and return the jokes collection."""

    try:
        # Cache the live collection so each request does not rebuild the client.
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
        client.admin.command("ping")
        return client["joke_database"]["jokes"]
    except errors.PyMongoError as exc:
        raise RuntimeError("database unavailable") from exc


class CollectionProxy:
    """Compatibility wrapper for callers that still expect a module-level collection."""

    def insert_one(self, *args, **kwargs):
        """Insert a single Mongo document through the cached collection."""
        return get_collection().insert_one(*args, **kwargs)

    def find(self, *args, **kwargs):
        """Return a Mongo cursor from the cached collection."""
        return get_collection().find(*args, **kwargs)

    def count_documents(self, *args, **kwargs):
        """Count Mongo documents through the cached collection."""
        return get_collection().count_documents(*args, **kwargs)


collection = CollectionProxy()


@app.route("/")
def dashboard():
    """Serve the frontend page."""

    # Makes sure that the URL route points to the homepage as detailed in index.html
    return send_from_directory(ROOT, "index.html")


@app.route("/api/analysis", methods=["POST"])
def add_analysis():  # pylint: disable=too-many-return-statements
    """Accept either an uploaded joke audio file or a JSON joke payload."""

    if request.is_json:
        data = request.get_json(force=True) or {}
    else:
        if "joke" not in request.files:
            return jsonify({"error": "missing input"}), 400
        joke = request.files["joke"]
        if not joke.filename:
            return jsonify({"error": "missing input"}), 400
        try:
            # Forward the browser upload stream directly so audio never needs local storage.
            joke.stream.seek(0)
            response = requests.post(
                ML_URL,
                files={
                    "joke": (joke.filename, joke.stream, joke.mimetype or "audio/webm")
                },
                timeout=45,
            )
        except requests.RequestException:
            response = None
        if response is None or response.status_code != 200:
            return jsonify({"error": "machine learning client failed"}), 500
        result = response.json()
        data = {
            "username": request.form.get("username", "").strip(),
            "text": result["text"],
            "classification": result["classification"],
            "funniness_score": result["score"],
        }

    required = ("text", "username", "classification", "funniness_score")
    if any(key not in data for key in required):
        return jsonify({"error": "missing submission fields"}), 400
    try:
        record = {
            "text": str(data["text"]).strip(),
            "username": str(data["username"]).strip(),
            "classification": int(data["classification"]),
            "funniness_score": int(data["funniness_score"]),
            "created_at": int(time() * 1000),
        }
    except (TypeError, ValueError):
        return jsonify({"error": "invalid submission fields"}), 400
    if not record["text"] or not record["username"]:
        return jsonify({"error": "missing submission fields"}), 400
    if record["classification"] == 0:
        return (
            jsonify(
                {
                    "status": "rejected",
                    "message": "That wasn't a joke.",
                    "data": record,
                }
            ),
            200,
        )
    try:
        insert_result = collection.insert_one(record)
        rank = next(
            (
                index
                for index, item in enumerate(
                    collection.find({}, {"_id": 1}).sort(SORT_ORDER), start=1
                )
                if item["_id"] == insert_result.inserted_id
            ),
            1,
        )
        total = collection.count_documents({})
    except RuntimeError:
        return jsonify({"error": "database unavailable"}), 500
    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "text": record["text"],
                    "username": record["username"],
                    "classification": record["classification"],
                    "funniness_score": record["funniness_score"],
                    "created_at": record["created_at"],
                },
                "rank": rank,
                "total": total,
            }
        ),
        201,
    )


@app.route("/api/analysis", methods=["GET"])
def get_analysis():
    """Return saved joke submissions for the frontend leaderboard."""

    try:
        results = [
            {
                "text": record.get("text", ""),
                "username": record.get("username", ""),
                "classification": record.get("classification", -1),
                "funniness_score": record.get("funniness_score", -1),
                "created_at": record.get("created_at", 0),
            }
            for record in collection.find().sort(SORT_ORDER)
        ]
    except RuntimeError:
        return jsonify({"error": "database unavailable"}), 500
    return jsonify({"results": results}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
