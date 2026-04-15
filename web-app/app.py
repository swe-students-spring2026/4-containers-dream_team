"""
Flask API server for analyzing text using a machine learning model.
This service determines whether input text contains humor and assigns a funniness score.
"""

from flask import Flask, request, jsonify, render_template
import requests

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
    Accepts audio input, runs ML analysis, and returns classification + score.
    """
    if "joke" not in request.files:
        return jsonify({"error": "missing input"}), 400
    joke = request.files["joke"]

    # Run joke to machine-learning-client where it is analyzed
    response = requests.post(
        "http://machine-learning-client:5001/process", jokes={"joke": joke}, timeout=45
    )

    # check it ran correctly
    if response.status_code != 200:
        return jsonify({"error": "machine learning client failed"}), 500

    # grab results from response
    result = response.json()

    # Build database record (to be saved later)
    record = {
        "text": result.text,
        "username": result.text,  # @TODO replace with real username field
        "classification": result.classification,
        "funniness_score": result.score,
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
