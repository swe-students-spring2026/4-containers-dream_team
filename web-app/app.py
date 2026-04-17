"""
Flask API server for analyzing text using a machine learning model.
This service determines whether input text contains humor and assigns a funniness score.
"""

import os
from flask import Flask, request, jsonify, render_template
import requests
from pymongo import MongoClient

mongo_url = os.getenv("MONGO_URI") or "mongodb://mongodb:27017"


# get the collection
client = MongoClient(mongo_url)
db = client["joke_database"]
collection = db["jokes"]

app = Flask(__name__)


@app.route("/")
def dashboard():
    """
    Render the main dashboard page.
    """

    return render_template("dashboard.html")


@app.route("/api/analysis", methods=["POST"])
def add_analysis():
    """
    Accepts audio input, runs ML analysis, and returns classification + score.
    """
    username = request.form.get("username", "").strip() or "Anonymous"

    if "joke" not in request.files:
        return jsonify({"error": "missing input"}), 400

    joke_file = request.files["joke"]

    if joke_file.filename == "":
        return jsonify({"error": "empty joke file"}), 400

    # Run joke to machine-learning-client where it is analyzed
    try:
        # send uploaded audio to ML service
        files = {
            "joke": (
                joke_file.filename,
                joke_file.stream,
                joke_file.mimetype or "audio/webm",
            )
        }

        response = requests.post(
            "http://machine-learning-client:5001/process",
            files=files,
            timeout=45,
        )
    except requests.RequestException:
        return jsonify({"error": "machine learning client unavailable"}), 500

    # check it ran correctly
    if response.status_code != 200:
        return jsonify({"error": "machine learning client failed"}), 500

    # grab results from response
    result = response.json()

    # Build database record (to be saved later)
    record = {
        "text": result.get("text", ""),
        "username": username,
        "classification": result.get("classification", "unknown"),
        "funniness_score": result.get("score", 0),
    }

    insert_result = collection.insert_one(record)
    record["_id"] = str(insert_result.inserted_id)

    return jsonify({"status": "success", "data": record}), 201


@app.route("/api/analysis", methods=["GET"])
def get_analysis():
    """
    Retrieve all stored analysis records.

    """

    results = list(collection.find())

    final_results = []

    for r in results:
        r["_id"] = str(r["_id"])
        final_results.append(r)

    return jsonify({"results": final_results}), 200


if __name__ == "__main__":
    # Runs Flask development server
    # NOTE: disable debug mode in production
    app.run(host="0.0.0.0", port=5000, debug=True)
