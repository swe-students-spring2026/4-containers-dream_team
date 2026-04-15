"Testing for joke_ranking module using mock api calls"

from unittest.mock import patch, MagicMock
import pytest
from joke_ranking import (
    generate_classification,
    generate_score,
    analyze_text,
    OutOfRangeError,
)


@patch("joke_ranking.client.models.generate_content")
def test_generate_classification_has_humor(mock_generate):
    "Testing for a potential test containing humor, which should return classification 1"
    mock_response = MagicMock()
    mock_response.text = "1"
    mock_generate.return_value = mock_response

    result = generate_classification("Why did the chicken cross the road?")

    assert result == 1
    mock_generate.assert_called_once()


@patch("joke_ranking.client.models.generate_content")
def test_generate_classification_humorless(mock_generate):
    "testing for a potential humorless text, which should return classification 0"
    mock_response = MagicMock()
    mock_response.text = "The result is 0."
    mock_generate.return_value = mock_response

    result = generate_classification("The sky is blue.")
    assert result == 0


@patch("joke_ranking.client.models.generate_content")
def test_generate_classification_out_of_range(mock_generate):
    "testing in case the api would return a wrong classification not in 0 or 1"
    mock_response = MagicMock()
    mock_response.text = "3"
    mock_generate.return_value = mock_response

    with pytest.raises(OutOfRangeError):
        generate_classification("Some text")


@patch("joke_ranking.client.models.generate_content")
def test_generate_score_valid(mock_generate):
    "testing for joke ranking which should return a score in range 1-100"
    mock_response = MagicMock()
    mock_response.text = "85"
    mock_generate.return_value = mock_response

    result = generate_score("A really funny joke")
    assert result == 85


@patch("joke_ranking.client.models.generate_content")
def test_generate_score_out_of_range_high(mock_generate):
    """testing for joke ranking return a score outside of the valid range,
    should raise an OutOfRange error"""
    mock_response = MagicMock()
    mock_response.text = "101"
    mock_generate.return_value = mock_response

    with pytest.raises(OutOfRangeError):
        generate_score("Too funny")


@patch("joke_ranking.client.models.generate_content")
def test_generate_score_no_digits(mock_generate):
    "testing in case api call return no score, should raise a value error"
    mock_response = MagicMock()
    mock_response.text = "I refuse to score this."
    mock_generate.return_value = mock_response

    with pytest.raises(ValueError):
        generate_score("Bad AI response")


@patch("joke_ranking.generate_score")
@patch("joke_ranking.generate_classification")
def test_analyze_text_with_humor(mock_classify, mock_score):
    """testing the analyze_text function recieving a funny piece of text,
    should return a tuple containing (1, score)"""
    mock_classify.return_value = 1
    mock_score.return_value = 90

    result = analyze_text("A joke")

    assert result == (1, 90)
    mock_classify.assert_called_once_with("A joke")
    mock_score.assert_called_once_with("A joke")


@patch("joke_ranking.generate_score")
@patch("joke_ranking.generate_classification")
def test_analyze_text_humorless(mock_classify, mock_score):
    """testing the analyze_text function recieving an unfunny piece of text,
    should return a tuple containing (0, -1)"""
    mock_classify.return_value = 0

    result = analyze_text("Boring text")

    assert result == (0, -1)
    mock_classify.assert_called_once_with("Boring text")
    mock_score.assert_not_called()
