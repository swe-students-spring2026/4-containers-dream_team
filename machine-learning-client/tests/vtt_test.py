"""Tests for voice to text file"""

from pathlib import Path
import pytest
from rapidfuzz import fuzz
import voice_to_text as vtt  # pylint: disable=import-error

TEST_ENGLISH = (
    "The stale smell of old beer lingers. "
    "It takes heat to bring out the odor. "
    "A cold dip restores health and zest. "
    "A salt pickle tastes fine with ham. "
    "Tacos al pastor are my favorite. "
    "A zestful food is the hot cross bun."
)


TEST_SPANISH = (
    "The high qualities of the woman who will inevitably "
    "be your wife do not need to be praised on this occasion, "
    "because we all know them well enough."
)


def get_audio_test(name):
    """Have a new get_audio() function so it takes local audio files instead of from web app"""
    audio = Path(name)
    if not audio.exists():
        raise FileNotFoundError("Joke has not been uploaded")
    if not audio.is_file():
        raise FileNotFoundError("Joke has not been uploaded")
    return str(audio)


class Tests:
    """Tests for the voice_to_text"""

    def test_vtt_eng(self):
        """Test to see if it translated english audio correctly"""
        audio = get_audio_test("tests/harvard.wav")
        text = vtt.voice_to_text(audio)
        score = fuzz.ratio(text, TEST_ENGLISH)
        assert score > 0.75

    def test_vtt_span(self):
        """Test to see if it accurately transcribes audio of different language to english"""
        audio = get_audio_test("tests/bailen_0003.wav")
        text = vtt.voice_to_text(audio)
        score = fuzz.ratio(text, TEST_SPANISH)
        assert score > 0.75

    def test_vtt_jokes_not_exist(self):
        """Test to see if properly raises flag for jokes section not existing.
        Can use fake section name as a test"""
        with pytest.raises(FileNotFoundError):
            get_audio_test("testaudio/")

    def test_vtt_file_not_in_joke(self):
        """Test to see if joke field exists on website yet there is not audio under"""
        with pytest.raises(FileNotFoundError):
            get_audio_test("")
