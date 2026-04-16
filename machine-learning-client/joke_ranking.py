"""
This module connects to the Google GenAI API to evaluate
if a piece of text has humor and then ranks how funny it is.
"""

import os

# Used to get a score for the joke
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


class OutOfRangeError(Exception):
    """Custom exception for the cases if Google AI returns an invalid score"""

    def __str__(self):
        return "Invalid Score was generated"


def generate_classification(text):
    """Given a string returns 0 if it's humorless or 1 if it has humor"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        config=types.GenerateContentConfig(
            system_instruction="""
            Return only 1 if the input contains 
            humor and only 0 if it is humorless"""
        ),
        contents=f"{text}",
    )

    classification = "".join(filter(str.isdigit, response.text))
    classification = int(classification)

    if classification not in (0, 1):
        raise OutOfRangeError

    return classification


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


def analyze_text(text):
    """Given text returns a tuple of two elements

    First element is either 0 or 1 where 0 corresponds to humorless text
    and 1 corresponds to funny text

    Second element is defaulted to -1 in case the text is not detected to be a joke
    In case where it is detected to be a joke the second element will correspond
    to a ranking of 1-100 based on how funny it is
    """

    score = -1
    classification = generate_classification(text)

    if classification:
        score = generate_score(text)

    return (classification, score)
