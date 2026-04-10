from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
joke = "They done messed up & selected me for jusry duty, SOMEBODY COMING HOME"

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        system_instruction="Treat the input as a joke. Return only a score 1 to 100 of the joke based on how funny it is"),
    contents=f"{joke}"
)

print(response.text)

