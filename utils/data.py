from datetime import datetime, timedelta
import random

def fetch_all(table):
    """Fetch all items from a DynamoDB table or mock table."""
    try:
        return table.scan().get("Items", [])
    except Exception:
        return []

def save_score(table, user_id: str, parsed: dict):
    """Save processed game score into game_scores table"""
    timestamp = datetime.utcnow().isoformat()
    item = {
        "user_id": user_id,
        "timestamp": timestamp,
        "raw_game": parsed["raw_game"],
        "game_number": parsed["game_number"],
        "score": parsed["score"],
        "secondary_metric": parsed.get("secondary_metric"),
        "metric": parsed["metric"],
        "game_date": datetime.utcnow().date().isoformat(),
    }
    table.put_item(Item=item)
    return item

def generate_test_data(table, user: str, game: str = "Pinpoint", start_day: int = 1, end_day: int = 7, extra_players=None):
    """Generate test data entries for one game with optional extra players"""
    if extra_players is None:
        extra_players = []

    for game_number in range(start_day, end_day + 1):
        timestamp = datetime.utcnow().replace(microsecond=game_number).isoformat()

        # Primary & secondary metrics
        secondary = None
        if game in ["Mini Sudoku", "Queens"]:
            score = random.randint(60, 600)
            secondary = random.randint(0, 5)
        elif game == "Pinpoint":
            score = random.randint(3, 10)
            secondary = random.randint(70, 100)
        elif game in ["Tango", "Zip"]:
            score = random.randint(10, 100)
            secondary = random.randint(0, 20)
        elif game == "Crossclimb":
            score = random.randint(3, 10)
        else:
            score = random.randint(1, 20)

        game_date = datetime.utcnow().date().isoformat()
        item = {
            "user_id": user,
            "timestamp": timestamp,
            "raw_game": game,
            "game_number": game_number,
            "score": score,
            "secondary_metric": secondary,
            "metric": "seconds" if game in ["Mini Sudoku", "Queens"] else "guesses" if game=="Pinpoint" else "points",
            "game_date": game_date
        }
        table.put_item(Item=item)

        # Extra players
        for p in extra_players:
            ts_extra = datetime.utcnow().replace(microsecond=game_number + 1000).isoformat()
            extra_score = score + random.randint(-10, 10)
            extra_secondary = secondary + random.randint(-2, 2) if secondary is not None else None
            item_extra = {
                "user_id": p,
                "timestamp": ts_extra,
                "raw_game": game,
                "game_number": game_number,
                "score": max(extra_score, 0),
                "secondary_metric": max(extra_secondary, 0) if extra_secondary is not None else None,
                "metric": "seconds" if game in ["Mini Sudoku", "Queens"] else "guesses" if game=="Pinpoint" else "points",
                "game_date": game_date
            }
            table.put_item(Item=item_extra)
    return True
