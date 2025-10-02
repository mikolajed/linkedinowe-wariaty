from datetime import datetime, timedelta
import random
from constants import GAMES

def fetch_all(table):
    try:
        return table.scan().get("Items", [])
    except Exception:
        return []

def save_score(table, user_id: str, parsed: dict):
    if parsed["raw_game"] not in GAMES:
        raise ValueError(f"Cannot save score: game '{parsed['raw_game']}' is not supported.")
    table.put_item(Item=parsed)
    return parsed

def generate_test_data(table, user: str, game: str = "Mini Sudoku", days: int = 7):
    if game not in GAMES:
        raise ValueError(f"Game {game} not allowed.")
    today = datetime.utcnow().date()
    for i in range(days):
        date = today - timedelta(days=i)
        if game in ["Pinpoint", "Crossclimb"]:
            score = random.randint(3, 10)
        elif game in ["Queens", "Mini Sudoku"]:
            score = random.randint(60, 600)
        elif game in ["Tango", "Zip"]:
            score = random.randint(10, 100)
        else:
            score = random.randint(1, 20)

        item = {
            "user_id": user,
            "raw_game": game,
            "score": score,
            "metric": "points/guesses/seconds",
            "game_number": i+1,
            "game_date": date.isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)
