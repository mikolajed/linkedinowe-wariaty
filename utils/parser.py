import re
from datetime import datetime

def parse_post(text: str):
    text = text.strip()
    # Mini Sudoku
    m = re.search(r"Mini Sudoku #(\d+)\s*\|\s*([\d:]+)", text)
    if m:
        game_number = int(m.group(1))
        mins, secs = map(int, m.group(2).split(":"))
        return {
            "raw_game": "Mini Sudoku",
            "score": mins*60 + secs,
            "metric": "seconds (lower better)",
            "game_number": game_number,
            "game_date": datetime.utcnow().date().isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
    # Pinpoint
    m = re.search(r"Pinpoint #(\d+)\s*\|\s*(\d+)\s*guesses", text, re.IGNORECASE)
    if m:
        return {
            "raw_game": "Pinpoint",
            "score": int(m.group(2)),
            "metric": "guesses (lower better)",
            "game_number": int(m.group(1)),
            "game_date": datetime.utcnow().date().isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
    # Queens
    m = re.search(r"Queens #(\d+)\s*\|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        mins, secs = map(int, m.group(2).split(":"))
        return {
            "raw_game": "Queens",
            "score": mins*60 + secs,
            "metric": "seconds (lower better)",
            "game_number": int(m.group(1)),
            "game_date": datetime.utcnow().date().isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
    # Crossclimb
    m = re.search(r"Crossclimb #(\d+)\s*\|\s*(\d+)\s*clues", text, re.IGNORECASE)
    if m:
        return {
            "raw_game": "Crossclimb",
            "score": int(m.group(2)),
            "metric": "clues (lower better)",
            "game_number": int(m.group(1)),
            "game_date": datetime.utcnow().date().isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
    # Tango
    m = re.search(r"Tango #(\d+)\s*\|\s*(\d+)\s*points", text, re.IGNORECASE)
    if m:
        return {
            "raw_game": "Tango",
            "score": int(m.group(2)),
            "metric": "points (higher better)",
            "game_number": int(m.group(1)),
            "game_date": datetime.utcnow().date().isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
    # Zip
    m = re.search(r"Zip #(\d+)\s*\|\s*(\d+)\s*points", text, re.IGNORECASE)
    if m:
        return {
            "raw_game": "Zip",
            "score": int(m.group(2)),
            "metric": "points (higher better)",
            "game_number": int(m.group(1)),
            "game_date": datetime.utcnow().date().isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }

    raise ValueError("Could not detect a supported game pattern.")
