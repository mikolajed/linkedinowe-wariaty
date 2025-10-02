import re

def parse_post(text: str):
    text = text.strip()
    result = {}

    # Mini Sudoku
    m = re.search(r"Mini Sudoku #(\d+)\s*\|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        mins, secs = map(int, m.group(2).split(":"))
        return {"raw_game": "Mini Sudoku", "score": mins*60 + secs, "metric": "seconds", "game_number": int(m.group(1))}

    # Pinpoint
    m = re.search(r"Pinpoint #(\d+)\s*\|\s*(\d+)\s*guesses", text, re.IGNORECASE)
    if m:
        res = {"raw_game": "Pinpoint", "score": int(m.group(2)), "metric": "guesses", "game_number": int(m.group(1))}
        acc = re.search(r"(\d+)%", text)
        if acc: res["secondary_metric"] = int(acc.group(1))
        return res

    # Queens
    m = re.search(r"Queens #(\d+)\s*\|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        mins, secs = map(int, m.group(2).split(":"))
        return {"raw_game": "Queens", "score": mins*60 + secs, "metric": "seconds", "game_number": int(m.group(1))}

    # Crossclimb
    m = re.search(r"Crossclimb #(\d+)\s*\|\s*(\d+)", text, re.IGNORECASE)
    if m:
        return {"raw_game": "Crossclimb", "score": int(m.group(2)), "metric": "seconds/clues", "game_number": int(m.group(1))}

    # Tango
    m = re.search(r"Tango #(\d+)\s*\|\s*([\d:]+|\d+)", text, re.IGNORECASE)
    if m:
        val = m.group(2)
        score = int(val) if ":" not in val else sum(int(x)*60**i for i,x in enumerate(reversed(val.split(":"))))
        return {"raw_game": "Tango", "score": score, "metric": "points", "game_number": int(m.group(1))}

    # Zip
    m = re.search(r"Zip #(\d+)\s*\|\s*([\d:]+|\d+)", text, re.IGNORECASE)
    if m:
        val = m.group(2)
        score = int(val) if ":" not in val else sum(int(x)*60**i for i,x in enumerate(reversed(val.split(":"))))
        res = {"raw_game": "Zip", "score": score, "metric": "seconds/points", "game_number": int(m.group(1))}
        back = re.search(r"(\d+)\s*backtrack", text, re.IGNORECASE)
        if back: res["secondary_metric"] = int(back.group(1))
        return res

    raise ValueError("Could not detect a supported game pattern.")
