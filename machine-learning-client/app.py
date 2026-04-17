"""Driver for machine learning"""

from flask import Flask, request, jsonify
from joke_ranking import analyze_text
from voice_to_text import voice_to_text as vtt

app = Flask(__name__)


@app.route("/process", methods=["POST"])
def analyze_joke():
    """Takes joke passed through front end driver and analyzes joke before returning."""
<<<<<<< HEAD
<<<<<<< HEAD

    if "joke" not in request.files:
        return jsonify({"error": "joke not passed through"}), 400
    

    # Keep the upload contract explicit for the web-app bridge.
    audio = request.files["joke"]

    if audio.filename == "":
        return jsonify({"error": "joke audio not saved properly"}), 400
    

    # Transcribe first, then run the transcript through the joke model.
=======
    if "files" not in request.files:
        return jsonify({"error": "joke not passed through"}), 404
    audio = request.files["files"]
>>>>>>> f47f154b4917615887cf23a5f39650af0b73b06d
    text = vtt(audio)
    classification, score = analyze_text(text)
    
    return jsonify({"text": text, "classification": classification, "score": score})
=======
    if "joke" not in request.files:
        return jsonify({"error": "joke not passed through"}), 400
    audio = request.files["joke"]
    text = vtt(audio)
    classification, score = analyze_text(text)
    return (
        jsonify({"text": text, "classification": classification, "score": score}),
        200,
    )
>>>>>>> 8d448b98c9384f4da61183540614ea7fa50eee08


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
