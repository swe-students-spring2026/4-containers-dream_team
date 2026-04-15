"""
Flask API server for analyzing text using a machine learning model.
This service determines whether input text contains humor and assigns a funniness score.
"""

from flask import Flask, request, jsonify, render_template
from machine_learning_client.joke_ranking import (
    analyze_text,
)  # pylint: disable=import-error

app = Flask(__name__)

# @TODO initialize db


@app.route("/")
def dashboard():
    """
    Render the main dashboard page.

    NOTE:
    This is a placeholder frontend route.
    Replace "dashboard.html" once frontend implementation is ready.
    """

    return render_template("dashboard.html")


@app.route("/api/analysis", methods=["POST"])
def add_analysis():
    """
    Accepts text input, runs ML analysis, and returns classification + score.

    Expected JSON payload:
    {
        "text": "your input text here"
    }
    """

    data = request.get_json(force=True)
    text = data.get("text")

    if not text:
        return jsonify({"error": "missing text"}), 400

    # Run ML model analysis
    classification, score = analyze_text(text)

    # Build database record (to be saved later)
    record = {
        "text": text,
        "username": text,  # @TODO replace with real username field
        "classification": classification,
        "funniness_score": score,
    }

    # @TODO save to db

    return jsonify({"status": "success", "data": record}), 201


@app.route("/api/analysis", methods=["GET"])
def get_analysis():
    """
    Retrieve all stored analysis records.

    @TODO:
    - Fetch records from database
    - Return them as JSON list
    """

    # Placeholder response until DB is implemented
    results = []

    return jsonify({"results": results}), 200


if __name__ == "__main__":
    # Runs Flask development server
    # NOTE: disable debug mode in production
    app.run(host="0.0.0.0", port=5000, debug=True)
