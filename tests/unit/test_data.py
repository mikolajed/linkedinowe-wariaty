import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from utils import data
from constants import PLAYERS, GAMES


@patch("utils.data.aws.get_ddb_table")
def test_fetch_all(mock_get_table):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": [{"id": "1"}, {"id": "2"}]}
    mock_get_table.return_value = mock_table

    result = data.fetch_all("raw_game_posts")
    assert len(result) == 2
    mock_get_table.assert_called_once_with(data._get_cfg(), "raw_game_posts")


@patch("utils.data.aws.get_ddb_table")
def test_save_score(mock_get_table):
    mock_table = MagicMock()
    mock_get_table.return_value = mock_table

    game_name = "Pinpoint"
    game_number = 42102025
    scores = [5, 95]
    units = ["guesses", "%"]

    result = data.save_score(
        "Mikuś",
        game_name=game_name,
        game_number=game_number,
        scores=scores,
        units=units,
        game_date="03-10-2025"
    )

    assert result["user_id"] == "Mikuś"
    assert result["game_name"] == game_name
    assert result["game_number"] == game_number
    assert result["scores"] == scores
    assert result["units"] == units
    assert result["game_date"] == "03-10-2025"

    mock_get_table.assert_called_once_with(data._get_cfg(), "game_scores")
    mock_table.put_item.assert_called_once()


@patch("utils.data.aws.get_ddb_table")
def test_save_post_without_score(mock_get_table):
    """Test saving a raw post that cannot be parsed (no score)"""
    mock_table = MagicMock()
    mock_get_table.return_value = mock_table

    raw_post_text = "This is a plain test post"
    result = data.save_post("Mikuś", raw_post_text)

    assert result["user_id"] == "Mikuś"
    assert result["raw_post"] == raw_post_text
    assert "timestamp" in result
    mock_table.put_item.assert_called_once_with(Item=result)


@patch("utils.data.parser.parse_post")
@patch("utils.data.aws.get_ddb_table")
def test_save_post_with_score(mock_get_table, mock_parse):
    """Test saving a raw post that contains a score"""
    mock_table = MagicMock()
    mock_get_table.return_value = mock_table

    raw_post_text = "Post with score"
    parsed = {
        "game_name": "Pinpoint",
        "game_number": 1,
        "scores": [5, 95],
        "units": ["guesses", "%"],
    }
    mock_parse.return_value = parsed

    result = data.save_post("Mikuś", raw_post_text)

    # raw post saved
    mock_table.put_item.assert_any_call(Item=result)
    # score saved to game_scores
    assert mock_table.put_item.call_count == 2


@patch("utils.data.aws.get_ddb_table")
def test_invalid_user_and_game(mock_get_table):
    mock_table = MagicMock()
    mock_get_table.return_value = mock_table

    game_name = "Pinpoint"
    game_number = 1
    scores = [5]
    units = ["guesses"]

    # invalid user
    with pytest.raises(ValueError):
        data.save_score("InvalidUser", game_name, game_number, scores, units)

    # invalid game
    with pytest.raises(ValueError):
        data.save_score("Mikuś", "InvalidGame", game_number, scores, units)


@patch("utils.data.aws.get_ddb_table")
def test_generate_test_data(mock_get_table):
    """Test generating test data for a range of dates"""
    mock_table = MagicMock()
    mock_get_table.return_value = mock_table

    start = date(2025, 10, 1)
    end = date(2025, 10, 3)

    result = data.generate_test_data(
        user="Mikuś",
        game="Pinpoint",
        start_date=start,
        end_date=end,
    )
    assert result is True
    assert mock_table.put_item.call_count == 3

    first_item = mock_table.put_item.call_args_list[0][1]["Item"]
    assert first_item["user_id"] == "Mikuś"
    assert first_item["game_name"] == "Pinpoint"
    assert first_item["game_date"] == "01-10-2025"
    assert "scores" in first_item
    assert "units" in first_item
