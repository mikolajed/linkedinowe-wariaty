import re

def parse_post(text: str):
    text = text.strip()

    def parse_time(val):
        if ":" in val:
            parts = [int(x) for x in val.split(":")]
            return sum(p * 60**i for i, p in enumerate(reversed(parts)))
        return int(val)

    # --- Mini Sudoku ---
    m = re.search(r"Mini Sudoku #(\d+)\s*\|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        return {
            "game_name": "Mini Sudoku",
            "game_number": int(m.group(1)),
            "scores": [parse_time(m.group(2))]
        }

    # --- Pinpoint ---
    m = re.search(r"Pinpoint #(\d+)\s*\|\s*(\d+)", text, re.IGNORECASE)
    if m:
        scores = [int(m.group(2))]
        acc = re.search(r"(\d+)%", text)
        if acc:
            scores.append(int(acc.group(1)))
        return {
            "game_name": "Pinpoint",
            "game_number": int(m.group(1)),
            "scores": scores
        }

    # --- Queens ---
    m = re.search(r"Queens #(\d+)\s*\|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        return {
            "game_name": "Queens",
            "game_number": int(m.group(1)),
            "scores": [parse_time(m.group(2))]
        }

    # --- Crossclimb ---
    m = re.search(r"Crossclimb #(\d+)\s*\|\s*([\d:]+|\d+)", text, re.IGNORECASE)
    if m:
        return {
            "game_name": "Crossclimb",
            "game_number": int(m.group(1)),
            "scores": [parse_time(m.group(2))]
        }

    # --- Tango ---
    m = re.search(r"Tango #(\d+)\s*\|\s*([\d:]+|\d+)", text, re.IGNORECASE)
    if m:
        return {
            "game_name": "Tango",
            "game_number": int(m.group(1)),
            "scores": [parse_time(m.group(2))]
        }

    # --- Zip ---
    m = re.search(r"Zip #(\d+)\s*\|\s*([\d:]+|\d+)", text, re.IGNORECASE)
    if m:
        scores = [parse_time(m.group(2))]
        back = re.search(r"(\d+)\s*(?:backtracks?|próby|\))", text, re.IGNORECASE)
        if back:
            scores.append(int(back.group(1)))
        return {
            "game_name": "Zip",
            "game_number": int(m.group(1)),
            "scores": scores
        }

    raise ValueError("Could not detect a supported game pattern.")
