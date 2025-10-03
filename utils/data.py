from datetime import datetime, timezone, timedelta
import random
import streamlit as st
from constants import PLAYERS, GAMES, SCORE_UNITS
from utils import parser, aws


def _get_cfg():
    """Return AWS config from Streamlit secrets."""
    return st.secrets.get("aws", {})


def fetch_all(table_name: str):
    """Fetch all items from a DynamoDB table."""
    AWS_CFG = _get_cfg()
    table = aws.get_ddb_table(AWS_CFG, table_name)  # should return boto3.Table
    try:
        return table.scan().get("Items", [])
    except Exception:
        return []


def save_post(user_id: str, raw_post: str):
    """Save a raw LinkedIn post and its parsed scores."""
    if user_id not in PLAYERS:
        raise ValueError(f"Invalid user '{user_id}', must be one of {PLAYERS}")

    AWS_CFG = _get_cfg()
    posts_table = aws.get_ddb_table(AWS_CFG, "raw_game_posts")

    timestamp = datetime.now(timezone.utc).isoformat()
    post_item = {
        "user_id": user_id,
        "raw_post": raw_post,
        "timestamp": timestamp,
    }
    posts_table.put_item(Item=post_item)

    try:
        parsed = parser.parse_post(raw_post)
        game_name = parsed["game_name"]
        if game_name in GAMES:
            units = SCORE_UNITS.get(game_name, ["points"])
            save_score(
                user_id=user_id,
                game_name=game_name,
                game_number=parsed["game_number"],
                scores=parsed["scores"],
                units=units,
                timestamp=timestamp,
            )
    except Exception:
        pass

    return post_item


def save_score(user_id: str, game_name: str, game_number: int, scores: list, units: list,
               game_date: str = None, timestamp: str = None):
    """Save a processed game score into 'game_scores'."""
    if user_id not in PLAYERS:
        raise ValueError(f"Invalid user '{user_id}', must be one of {PLAYERS}")
    if game_name not in GAMES:
        raise ValueError(f"Invalid game '{game_name}', must be one of {GAMES}")

    AWS_CFG = _get_cfg()
    scores_table = aws.get_ddb_table(AWS_CFG, "game_scores")

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if game_date is None:
        game_date = datetime.now(timezone.utc).strftime("%d-%m-%Y")

    item = {
        "user_id": user_id,
        "timestamp": timestamp,
        "game_name": game_name,
        "game_number": game_number,
        "scores": scores,
        "units": units,
        "game_date": game_date,
    }
    scores_table.put_item(Item=item)
    return item


def generate_test_data(user: str, game: str = "Pinpoint",
                       start_date: datetime = None, end_date: datetime = None):
    """
    Generate test data entries for one game for a single user into 'game_scores'.
    Each day in the date range becomes an entry.
    """
    if user not in PLAYERS:
        raise ValueError(f"Invalid user '{user}', must be one of {PLAYERS}")
    if game not in GAMES:
        raise ValueError(f"Invalid game '{game}', must be one of {GAMES}")

    if start_date is None:
        start_date = datetime.now().date()
    if end_date is None:
        end_date = start_date

    AWS_CFG = _get_cfg()
    scores_table = aws.get_ddb_table(AWS_CFG, "game_scores")

    current_date = start_date
    while current_date <= end_date:
        game_number = int(current_date.strftime("%d%m%Y"))
        game_date_str = current_date.strftime("%d-%m-%Y")

        scores, units = [], []

        # Assign scores and units based on constants
        if game in ["Mini Sudoku", "Queens"]:
            scores.append(random.randint(60, 600))
            units.append(SCORE_UNITS[game][0])
        elif game == "Pinpoint":
            scores.append(random.randint(3, 10))
            scores.append(random.randint(70, 100))
            units.extend(SCORE_UNITS[game])
        elif game in ["Tango", "Zip"]:
            scores.append(random.randint(10, 100))
            scores.append(random.randint(0, 20))
            units.extend(SCORE_UNITS[game])
        elif game == "Crossclimb":
            scores.append(random.randint(3, 10))
            units.extend(SCORE_UNITS[game])
        else:
            scores.append(random.randint(1, 20))
            units.extend(SCORE_UNITS.get(game, ["points"]))

        timestamp = datetime.combine(current_date, datetime.min.time()).replace(microsecond=0).isoformat()
        item = {
            "user_id": user,
            "timestamp": timestamp,
            "game_name": game,
            "game_number": game_number,
            "scores": scores,
            "units": units,
            "game_date": game_date_str,
        }
        scores_table.put_item(Item=item)

        current_date += timedelta(days=1)

    return True
