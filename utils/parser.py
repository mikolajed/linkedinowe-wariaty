import re

def parse_post(text: str):
    text = text.strip()
    m = re.search(r"Pinpoint #\d+ \|\s*(\d+)\s*guesses", text, re.IGNORECASE)
    if m: return {"game": "Pinpoint", "score": int(m.group(1)), "metric": "guesses (lower better)"}
    m = re.search(r"Queens #\d+ \|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        mins, secs = map(int, m.group(1).split(":"))
        return {"game": "Queens", "score": mins*60 + secs, "metric": "seconds (lower better)"}
    m = re.search(r"Crossclimb #\d+ \|\s*(\d+)\s*clues", text, re.IGNORECASE)
    if m: return {"game": "Crossclimb", "score": int(m.group(1)), "metric": "clues (lower better)"}
    m = re.search(r"Tango #\d+ \|\s*(\d+)\s*points", text, re.IGNORECASE)
    if m: return {"game": "Tango", "score": int(m.group(1)), "metric": "points (higher better)"}
    raise ValueError("Could not detect a supported game pattern.")
