"""File to take web apps voice files and convert it to text"""
import os
from flask import Flask, request
import assemblyai as aai

app = Flask(__name__)
aai.settings.api_key = os.getenv("VTT_API_KEY")

@app.post("/")
def voice_to_text():
    """Handle case where jokes are not passed and transcribe when passed"""
    if "joke" not in request.files:
        raise FileNotFoundError("No jokes have been uploaded")
    audio = request.files["joke"]
    if audio.filename == '':
        raise FileNotFoundError("Joke has not been uploaded")

    #takes the joke audio, and uploads to assemblyAI, also translates to english when necessary
    config = aai.TranscriptionConfig(
        speech_models=["universal-3-pro", "universal-2"],
        language_detection=True,
        speech_understanding={
        "request": {
            "translation": {
                "target_languages": ["en"],
                "formal": True
                }
            }
        }
    )

    transcript = aai.Transcriber(config=config).transcribe(audio)

    if transcript.status == "error":
        raise RuntimeError(f"Transcription failed: {transcript.error}")


    return transcript.translated_texts["en"]
