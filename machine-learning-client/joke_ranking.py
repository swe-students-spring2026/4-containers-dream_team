"""
This module connects to the Google GenAI API to evaluate and rank jokes.
"""

import os

# Used to load environment credentials
from dotenv import load_dotenv

# Used to get a score for the joke
from google import genai
from google.genai import types

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


class OutOfRangeError(Exception):
    """Custom exception for the cases if Google AI returns an invalid score"""

    def __str__(self):
        return "Invalid Score was generated"


# JOKE = "They done messed up & selected me for jusry duty, SOMEBODY COMING HOME"


def generate_score(joke):
    """Given a string(joke) generates a score 1-100 based on how funny it is"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        config=types.GenerateContentConfig(
            system_instruction="""Treat the input as a joke.
              Return only a score 1 to 100 of the joke based on how funny it is"""
        ),
        contents=f"{joke}",
    )

    score = "".join(filter(str.isdigit, response.text))
    score = int(score)

    if score < 1 or score > 100:
        raise OutOfRangeError

    return score
