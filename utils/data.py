from datetime import datetime, timedelta
import random
import pandas as pd

def fetch_all(table):
    """Fetch all items from DynamoDB table"""
    try:
        return table.scan().get("Items", [])
    except Exception:
        return []

def save_score(table, user_id: str, parsed: dict):
    """
    Save processed game score into `game_scores` table
    """
    from constants import GAMES

    if parsed["raw_game"] not in GAMES:
        raise ValueError(f"Cannot save score: game '{parsed['raw_game']}' not supported.")

    timestamp = datetime.utcnow().isoformat()

    item = {
        "user_id": user_id,             # Partition key
        "timestamp": timestamp,         # Sort key
        "raw_game": parsed["raw_game"],
        "game_number": parsed["game_number"],
        "score": parsed["score"],
        "metric": parsed["metric"],
        "secondary_metric": parsed.get("secondary_metric", None),
        "game_date": parsed["game_date"],
    }

    table.put_item(Item=item)
    return item


def save_raw_post(table, user_id: str, raw_post: str, game: str = None, game_number: int = None):
    """
    Save raw LinkedIn post into `raw_game_posts` table
    """
    timestamp = datetime.utcnow().isoformat()
    item = {
        "user_id": user_id,
        "timestamp": timestamp,     # Sort key
        "raw_post": raw_post,
        "game": game,
        "game_number": game_number,
    }
    table.put_item(Item=item)
    return item


def generate_test_data(table, user: str, game: str = "Pinpoint", days: int = 7):
    """
    Generate test data for `game_scores` table
    """
    today = datetime.utcnow().date()
    for i in range(days):
        date = today - timedelta(days=i)
        timestamp = (datetime.utcnow() - timedelta(days=i)).replace(hour=12, minute=0, second=0).isoformat()

        # Random metric generation
        if game in ["Pinpoint", "Crossclimb"]:
            score = random.randint(3, 10)
        elif game in ["Queens", "Mini Sudoku"]:
            score = random.randint(60, 600)
        elif game in ["Tango", "Zip"]:
            score = random.randint(10, 100)
        else:
            score = random.randint(1, 20)

        secondary = None
        if game == "Zip":
            secondary = random.randint(0, 20)
        elif game == "Pinpoint":
            secondary = random.randint(70, 100)  # accuracy %

        item = {
            "user_id": user,
            "timestamp": timestamp,
            "raw_game": game,
            "game_number": i + 1,
            "score": score,
            "metric": "seconds" if game not in ["Pinpoint"] else "guesses",
            "secondary_metric": secondary,
            "game_date": date.isoformat()
        }
        table.put_item(Item=item)
    return True
