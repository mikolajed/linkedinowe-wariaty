from datetime import datetime, timedelta
import random
import pandas as pd

def fetch_all(table):
    try:
        return table.scan().get("Items", [])
    except Exception:
        return []

def save_score(table, user: str, parsed: dict):
    item = {
        "user_id": user,
        "game_date": f"{parsed['game']}_{datetime.utcnow().date().isoformat()}",
        "score": parsed["score"],
        "metric": parsed["metric"],
        "timestamp": datetime.utcnow().isoformat(),
        "raw_game": parsed["game"],
    }
    table.put_item(Item=item)
    return item

def generate_test_data(table, user: str, game: str = "Pinpoint", days: int = 7):
    today = datetime.utcnow().date()
    for i in range(days):
        date = today - timedelta(days=i)

        # Different score types depending on the game
        if game in ["Pinpoint", "Crossclimb"]:
            score = random.randint(3, 10)  # guesses or clues
        elif game in ["Queens", "Mini Sudoku"]:
            score = random.randint(60, 600)  # seconds
        elif game in ["Tango", "Zip"]:
            score = random.randint(10, 100)  # points
        else:
            score = random.randint(1, 20)  # fallback

        item = {
            "user_id": user,
            "game_date": f"{game}_{date.isoformat()}",
            "score": score,
            "metric": "points/guesses/seconds",
            "timestamp": (datetime.utcnow() - timedelta(days=i)).replace(hour=12, minute=0, second=0).isoformat(),
            "raw_game": game,
        }
        table.put_item(Item=item)
    return True
