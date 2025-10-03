import re

def parse_post(text: str):
    text = text.strip()

    # --- Mini Sudoku ---
    # Example: "Mini Sudoku #52 | 6:29"
    m = re.search(r"Mini Sudoku #(\d+)\s*\|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        val = m.group(2)
        parts = [int(x) for x in val.split(":")]
        score = sum(p * 60**i for i, p in enumerate(reversed(parts)))
        return {"raw_game": "Mini Sudoku", "score": score, "metric": "seconds", "game_number": int(m.group(1))}

    # --- Pinpoint ---
    # Example: "Pinpoint #520 | 1 guess" OR "Pinpoint #520 | 3 próby"
    m = re.search(r"Pinpoint #(\d+)\s*\|\s*(\d+)", text, re.IGNORECASE)
    if m:
        res = {
            "raw_game": "Pinpoint",
            "score": int(m.group(2)),
            "metric": "guesses",
            "game_number": int(m.group(1))
        }
        # Look for percentage anywhere (e.g. "85%")
        acc = re.search(r"(\d+)%", text)
        if acc:
            res["secondary_metric"] = int(acc.group(1))
        return res

    # --- Queens ---
    # Example: "Queens #520 | 1:57"
    m = re.search(r"Queens #(\d+)\s*\|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        val = m.group(2)
        parts = [int(x) for x in val.split(":")]
        score = sum(p * 60**i for i, p in enumerate(reversed(parts)))
        return {"raw_game": "Queens", "score": score, "metric": "seconds", "game_number": int(m.group(1))}

    # --- Crossclimb ---
    # Example: "Crossclimb #123 | 8:12" OR "Crossclimb #123 | 12"
    m = re.search(r"Crossclimb #(\d+)\s*\|\s*([\d:]+|\d+)", text, re.IGNORECASE)
    if m:
        val = m.group(2)
        if ":" in val:
            parts = [int(x) for x in val.split(":")]
            score = sum(p * 60**i for i, p in enumerate(reversed(parts)))
        else:
            score = int(val)
        return {"raw_game": "Crossclimb", "score": score, "metric": "seconds/clues", "game_number": int(m.group(1))}

    # --- Tango ---
    # Example: "Tango #360 | 2:17" OR "Tango #360 | 35"
    m = re.search(r"Tango #(\d+)\s*\|\s*([\d:]+|\d+)", text, re.IGNORECASE)
    if m:
        val = m.group(2)
        if ":" in val:
            parts = [int(x) for x in val.split(":")]
            score = sum(p * 60**i for i, p in enumerate(reversed(parts)))
        else:
            score = int(val)
        return {"raw_game": "Tango", "score": score, "metric": "points", "game_number": int(m.group(1))}

    # --- Zip ---
    # Example: "Zip #199 | 0:36 🏁 With 18 backtracks" OR "Zip #199 | 45 (3 próby)"
    m = re.search(r"Zip #(\d+)\s*\|\s*([\d:]+|\d+)", text, re.IGNORECASE)
    if m:
        val = m.group(2)
        if ":" in val:
            parts = [int(x) for x in val.split(":")]
            score = sum(p * 60**i for i, p in enumerate(reversed(parts)))
        else:
            score = int(val)
        res = {
            "raw_game": "Zip",
            "score": score,
            "metric": "seconds/points",
            "game_number": int(m.group(1))
        }
        # Secondary: look for trailing number before "backtrack" or in parentheses
        back = re.search(r"(\d+)\s*(?:backtracks?|próby|\))", text, re.IGNORECASE)
        if back:
            res["secondary_metric"] = int(back.group(1))
        return res

    raise ValueError("Could not detect a supported game pattern.")
