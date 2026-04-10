#File to take web apps voice files and convert it to text
from flask import Flask, request
import pymongo
import os
import assemblyai as aai

app = Flask(__name__)
aai.settings.api_key = "693286ac70e740a2b438334875176dca"

@app.get("/")
def voice_to_text():
    if "joke" not in request.files:
        FileNotFoundError("No jokes have been uploaded")
    audio = request.files["joke"]
    if audio.filename == '':
        FileNotFoundError("Joke has not been uploaded")

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



