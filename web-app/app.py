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
ML_URL = "http://machine-learning-client:5001/process"
MONGO_URI = os.getenv("MONGO_URI") or "mongodb://mongodb:27017"


@lru_cache(maxsize=1)
def get_collection():
    """Connect to MongoDB and return the jokes collection."""

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1000)
        client.admin.command("ping")
        return client["joke_database"]["jokes"]
    except errors.PyMongoError as exc:
        raise RuntimeError("database unavailable") from exc


def serialize_record(record):
    """Convert a Mongo document into frontend-safe JSON."""

    return {
        "id": str(record["_id"]),
        "text": record.get("text", ""),
        "username": record.get("username", ""),
        "classification": record.get("classification", -1),
        "funniness_score": record.get("funniness_score", -1),
        "created_at": record.get("created_at", 0),
    }


def sorted_results(collection):
    """Return saved jokes ordered from funniest to least funny."""

    cursor = collection.find().sort(
        [("funniness_score", DESCENDING), ("created_at", DESCENDING)]
    )
    return [serialize_record(record) for record in cursor]


@app.route("/")
def dashboard():
    """Serve the frontend page."""

    return send_from_directory(ROOT, "index.html")


def create_app():
    """Provide the Flask app for tests and external runners."""

    return app


def save_submission(data):
    """Validate and persist a JSON joke submission."""

    required = ("text", "username", "classification", "funniness_score")
    if any(key not in data for key in required):
        return jsonify({"error": "missing submission fields"}), 400
    try:
        collection = get_collection()
    except RuntimeError:
        return jsonify({"error": "database unavailable"}), 500
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
    insert_result = collection.insert_one(record)
    results = sorted_results(collection)
    rank = next(
        (
            index
            for index, item in enumerate(results, start=1)
            if item["id"] == str(insert_result.inserted_id)
        ),
        len(results),
    )
    return (
        jsonify(
            {
                "status": "success",
                "data": serialize_record({**record, "_id": insert_result.inserted_id}),
                "rank": rank,
                "total": len(results),
            }
        ),
        201,
    )


def transcribe_upload():
    """Send uploaded joke audio to the ML service for transcription and scoring."""

    if "joke" not in request.files:
        return jsonify({"error": "missing input"}), 400
    joke = request.files["joke"]
    if not joke.filename:
        return jsonify({"error": "missing input"}), 400
    try:
        joke.stream.seek(0)
        response = requests.post(
            ML_URL,
            files={"joke": (joke.filename, joke.stream, joke.mimetype or "audio/webm")},
            timeout=45,
        )
    except requests.RequestException:
        response = None

    if response is None or response.status_code != 200:
        return jsonify({"error": "machine learning client failed"}), 500

    result = response.json()
    record = {
        "text": result["text"],
        "classification": result["classification"],
        "funniness_score": result["score"],
    }
    return jsonify({"status": "success", "data": record}), 200


@app.route("/api/analysis", methods=["POST"])
def add_analysis():
    """Accept either an uploaded joke audio file or a JSON joke payload."""

    if request.is_json:
        return save_submission(request.get_json(force=True) or {})
    return transcribe_upload()


@app.route("/api/analysis", methods=["GET"])
def get_analysis():
    """Return saved joke submissions for the frontend leaderboard."""

    try:
        collection = get_collection()
    except RuntimeError:
        return jsonify({"error": "database unavailable"}), 500
    results = sorted_results(collection)
    return jsonify({"results": results}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
