from datetime import datetime, timezone
import random
from constants import PLAYERS, GAMES, SCORE_UNITS

def fetch_all(table):
    """Fetch all items from a DynamoDB table or mock table."""
    try:
        return table.scan().get("Items", [])
    except Exception:
        return []

def save_score(table, user_id: str, parsed: dict, game_date: str = None):
    """
    Save processed game score into game_scores table.
    
    Parameters:
    - table: DynamoDB or mock table
    - user_id: must be in PLAYERS
    - parsed: dict with keys 'raw_game', 'game_number', 'scores', 'units'
    - game_date: optional, format 'dd-mm-yyyy'. Defaults to today UTC
    """
    if user_id not in PLAYERS:
        raise ValueError(f"Invalid user '{user_id}', must be one of {PLAYERS}")
    if parsed['raw_game'] not in GAMES:
        raise ValueError(f"Invalid game '{parsed['raw_game']}', must be one of {GAMES}")

    timestamp = datetime.now(timezone.utc).isoformat()
    if game_date is None:
        game_date = datetime.now(timezone.utc).strftime("%d-%m-%Y")

    item = {
        "user_id": user_id,
        "timestamp": timestamp,
        "raw_game": parsed["raw_game"],
        "game_number": parsed["game_number"],
        "scores": parsed.get("scores", []),
        "units": parsed.get("units", []),
        "game_date": game_date
    }
    table.put_item(Item=item)
    return item

def generate_test_data(table, user: str, game: str = "Pinpoint", start_day: int = 1, end_day: int = 7, game_date: str = None):
    """
    Generate test data entries for one game for a single user.
    - game_date: optional, 'dd-mm-yyyy'. Defaults to today UTC
    """
    if user not in PLAYERS:
        raise ValueError(f"Invalid user '{user}', must be one of {PLAYERS}")
    if game not in GAMES:
        raise ValueError(f"Invalid game '{game}', must be one of {GAMES}")

    if game_date is None:
        game_date = datetime.now(timezone.utc).strftime("%d-%m-%Y")

    for game_number in range(start_day, end_day + 1):
        # Primary & secondary scores
        scores = []
        units = []

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

        timestamp = datetime.now(timezone.utc).replace(microsecond=game_number).isoformat()
        item = {
            "user_id": user,
            "timestamp": timestamp,
            "raw_game": game,
            "game_number": game_number,
            "scores": scores,
            "units": units,
            "game_date": game_date
        }
        table.put_item(Item=item)

    return True
