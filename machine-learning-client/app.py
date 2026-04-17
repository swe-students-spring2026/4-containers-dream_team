"""Driver for machine learning"""

from flask import Flask, request, jsonify
from joke_ranking import analyze_text
from voice_to_text import voice_to_text as vtt

app = Flask(__name__)


@app.route("/process", methods=["POST"])
def analyze_joke():
    """Takes joke passed through front end driver and analyzes joke before returning."""
    if "joke" not in request.files:
        return jsonify({"error": "joke not passed through"}), 400
    audio = request.files["joke"]
    text = vtt(audio)
    classification, score = analyze_text(text)
    return (
        jsonify({"text": text, "classification": classification, "score": score}),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
