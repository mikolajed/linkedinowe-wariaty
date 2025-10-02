import re
from datetime import datetime

def parse_post(text: str):
    """
    Parse a LinkedIn game post into structured data.
    Supports: Pinpoint, Queens, Crossclimb, Tango, Mini Sudoku, Zip
    """
    text = text.strip()

    # Pinpoint
    m = re.search(r"Pinpoint #\d+ \|\s*(\d+)\s*guesses", text, re.IGNORECASE)
    if m:
        return {"game": "Pinpoint", "score": int(m.group(1)), "metric": "guesses (lower better)"}

    # Queens
    m = re.search(r"Queens #\d+ \|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        mins, secs = map(int, m.group(1).split(":"))
        return {"game": "Queens", "score": mins*60 + secs, "metric": "seconds (lower better)"}

    # Crossclimb
    m = re.search(r"Crossclimb #\d+ \|\s*(\d+)\s*clues", text, re.IGNORECASE)
    if m:
        return {"game": "Crossclimb", "score": int(m.group(1)), "metric": "clues (lower better)"}

    # Tango
    m = re.search(r"Tango #\d+ \|\s*(\d+)\s*points", text, re.IGNORECASE)
    if m:
        return {"game": "Tango", "score": int(m.group(1)), "metric": "points (higher better)"}

    # Mini Sudoku
    m = re.search(r"Mini Sudoku #\d+ \|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        mins, secs = map(int, m.group(1).split(":"))
        return {"game": "Mini Sudoku", "score": mins*60 + secs, "metric": "seconds (lower better)"}

    # Zip
    m = re.search(r"Zip #\d+ \|\s*(\d+)\s*words", text, re.IGNORECASE)
    if m:
        return {"game": "Zip", "score": int(m.group(1)), "metric": "words (higher better)"}

    raise ValueError("Could not detect a supported game pattern.")
