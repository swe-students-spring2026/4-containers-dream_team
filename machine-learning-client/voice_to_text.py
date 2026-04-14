"""File to take web apps voice files and convert it to text"""

import os
from flask import Flask, request
import assemblyai as aai

app = Flask(__name__)
aai.settings.api_key = os.getenv("VTT_API_KEY")

"""Helper function to retrieve audio"""
def get_audio():
    if "joke" not in request.files:
        raise FileNotFoundError("No jokes have been uploaded")
    audio = request.files["joke"]
    if audio.filename == "":
        raise FileNotFoundError("Joke has not been uploaded")
    return audio

@app.post("/")
def voice_to_text(audio):
    """Transcribe jokes passed"""
    # takes the joke audio, and uploads to assemblyAI, also translates to english when necessary
    config = aai.TranscriptionConfig(
        speech_models=["universal-3-pro", "universal-2"],
        language_detection=True,
        speech_understanding={
            "request": {"translation": {"target_languages": ["en"], "formal": True}}
        },
    )

    transcript = aai.Transcriber(config=config).transcribe(audio)

    if transcript.status == "error":
        raise RuntimeError(f"Transcription failed: {transcript.error}")
    if transcript.translated_texts == None:
        return transcript.text
    else:
        return transcript.translated_texts["en"]
