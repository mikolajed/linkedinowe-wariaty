import re

def parse_post(text: str):
    """
    Parse a LinkedIn game post and extract numeric metrics.
    Returns a dict with:
    - raw_game
    - score (primary numeric metric)
    - metric (description)
    - game_number
    - optional secondary_metric
    """

    text = text.strip()
    result = {}

    # --- Mini Sudoku ---
    m = re.search(r"Mini Sudoku #(\d+)\s*\|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        mins, secs = map(int, m.group(2).split(":"))
        result = {
            "raw_game": "Mini Sudoku",
            "score": mins*60 + secs,
            "metric": "seconds",
            "game_number": int(m.group(1))
        }
        return result

    # --- Pinpoint ---
    m = re.search(r"Pinpoint #(\d+)\s*\|\s*(\d+)\s*guesses", text, re.IGNORECASE)
    if m:
        result = {
            "raw_game": "Pinpoint",
            "score": int(m.group(2)),
            "metric": "guesses",
            "game_number": int(m.group(1))
        }
        # Optional: try to extract accuracy %
        acc_match = re.search(r"(\d+)%", text)
        if acc_match:
            result["secondary_metric"] = int(acc_match.group(1))
        return result

    # --- Queens ---
    m = re.search(r"Queens #(\d+)\s*\|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        mins, secs = map(int, m.group(2).split(":"))
        result = {
            "raw_game": "Queens",
            "score": mins*60 + secs,
            "metric": "seconds",
            "game_number": int(m.group(1))
        }
        return result

    # --- Crossclimb ---
    m = re.search(r"Crossclimb #(\d+)\s*\|\s*(\d+)", text, re.IGNORECASE)
    if m:
        result = {
            "raw_game": "Crossclimb",
            "score": int(m.group(2)),
            "metric": "seconds/clues",
            "game_number": int(m.group(1))
        }
        return result

    # --- Tango ---
    m = re.search(r"Tango #(\d+)\s*\|\s*([\d:]+|\d+)", text, re.IGNORECASE)
    if m:
        value = m.group(2)
        if ":" in value:
            mins, secs = map(int, value.split(":"))
            score = mins*60 + secs
        else:
            score = int(value)
        result = {
            "raw_game": "Tango",
            "score": score,
            "metric": "points",
            "game_number": int(m.group(1))
        }
        return result

    # --- Zip ---
    m = re.search(r"Zip #(\d+)\s*\|\s*([\d:]+|\d+)", text, re.IGNORECASE)
    if m:
        value = m.group(2)
        if ":" in value:
            mins, secs = map(int, value.split(":"))
            score = mins*60 + secs
        else:
            score = int(value)
        result = {
            "raw_game": "Zip",
            "score": score,
            "metric": "seconds/points",
            "game_number": int(m.group(1))
        }
        # Optional: try to extract backtracks
        backtrack_match = re.search(r"(\d+)\s*backtrack", text, re.IGNORECASE)
        if backtrack_match:
            result["secondary_metric"] = int(backtrack_match.group(1))
        return result

    raise ValueError("Could not detect a supported game pattern.")
