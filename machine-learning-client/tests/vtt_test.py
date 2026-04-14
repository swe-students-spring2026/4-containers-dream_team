import pytest
from rapidfuzz import fuzz
import voice_to_text as vtt
from pathlib import Path

"""Set up transcribed texts to compare to"""

test_english = "The stale smell of old beer lingers. " \
"It takes heat to bring out the odor. " \
"A cold dip restores health and zest. "\
"A salt pickle tastes fine with ham. " \
"Tacos al pastor are my favorite. " \
"A zestful food is the hot cross bun."


test_spanish = "The high qualities of the woman who will inevitably " \
"be your wife do not need to be praised on this occasion, " \
"because we all know them well enough."


"""Have a new get_audio() function so it takes local audio files instead of from web app"""
def get_audio_test(name):
    audio = Path(name)
    if not audio.exists():
        raise FileNotFoundError("Joke has not been uploaded")
    if not audio.is_file():
        raise FileNotFoundError("Joke has not been uploaded")
    return str(audio)

class Tests:
    """Test to see if it translated english audio correctly"""
    def test_vtt_eng(self):
        audio = get_audio_test("tests/harvard.wav")
        text = vtt.voice_to_text(audio)
        score = fuzz.ratio(text, test_english)
        assert score > .75

    """Test to see if it accurately transcribes audio of different language to english"""
    def test_vtt_span(self):
        audio = get_audio_test("tests/bailen_0003.wav")
        text = vtt.voice_to_text(audio)
        score = fuzz.ratio(text, test_spanish)
        assert score > .75

    """Test to see if properly raises flag for jokes section not existing.
    Can use fake section name as a test"""
    def test_vtt_jokes_not_exist(self):
        with pytest.raises(FileNotFoundError):
            audio = get_audio_test("testaudio/")

    """Test to see if joke field exists on website yet there is not audio under"""
    def test_vtt_file_not_in_joke(self):
        with pytest.raises(FileNotFoundError):
            audio = get_audio_test("")
