import pytest
from utils.parser import parse_post

@pytest.mark.parametrize(
    "text, expected",
    [
        # ----------------------------
        # Mini Sudoku
        # ----------------------------
        ("Mini Sudoku #123 | 2:45", {"raw_game": "Mini Sudoku", "score": 165, "game_number": 123}),
        ("Mini Sudoku #42 | 0:59", {"raw_game": "Mini Sudoku", "score": 59, "game_number": 42}),
        ("Mini Sudoku #77 | 1:02:03", {"raw_game": "Mini Sudoku", "score": 3723, "game_number": 77}),
        ("Mini Sudoku #52 | 6:29 and flawless ✏️\nThe classic game.\nlnkd.in/minisudoku.",
         {"raw_game": "Mini Sudoku", "score": 389, "game_number": 52}),

        # ----------------------------
        # Pinpoint
        # ----------------------------
        ("Pinpoint #42 | 5 guesses", {"raw_game": "Pinpoint", "score": 5, "game_number": 42}),
        ("Pinpoint #43 | 1 guess", {"raw_game": "Pinpoint", "score": 1, "game_number": 43}),
        ("Pinpoint #100 | 3 guesses | 95% accuracy", {"raw_game": "Pinpoint", "score": 3, "secondary_metric": 95, "game_number": 100}),
        ("Pinpoint #101 | 4 próby | 88%", {"raw_game": "Pinpoint", "score": 4, "secondary_metric": 88, "game_number": 101}),
        ("Pinpoint #520 | 1 guess\n1️⃣ | 100% match 📌\nlnkd.in/pinpoint.",
         {"raw_game": "Pinpoint", "score": 1, "secondary_metric": 100, "game_number": 520}),

        # ----------------------------
        # Queens
        # ----------------------------
        ("Queens #10 | 1:30", {"raw_game": "Queens", "score": 90, "game_number": 10}),
        ("Queens #11 | 12:05", {"raw_game": "Queens", "score": 725, "game_number": 11}),
        ("Queens #520 | 1:57\nFirst 👑s: 🟦 🟩 🟫\nlnkd.in/queens.",
         {"raw_game": "Queens", "score": 117, "game_number": 520}),

        # ----------------------------
        # Crossclimb
        # ----------------------------
        ("Crossclimb #15 | 8", {"raw_game": "Crossclimb", "score": 8, "game_number": 15}),
        ("Crossclimb #16 | 8:12", {"raw_game": "Crossclimb", "score": 492, "game_number": 16}),
        ("Crossclimb #520 | 3:13\nFill order: 1️⃣ 2️⃣ 3️⃣ 5️⃣ 4️⃣ 🔼 🔽 🪜\nlnkd.in/crossclimb.",
         {"raw_game": "Crossclimb", "score": 193, "game_number": 520}),

        # ----------------------------
        # Tango
        # ----------------------------
        ("Tango #5 | 45", {"raw_game": "Tango", "score": 45, "game_number": 5}),
        ("Tango #6 | 1:30", {"raw_game": "Tango", "score": 90, "game_number": 6}),
        ("Tango #7 | 1:02:03", {"raw_game": "Tango", "score": 3723, "game_number": 7}),
        ("Tango #360 | 2:17 and flawless\nFirst 5 placements:\nlnkd.in/tango.",
         {"raw_game": "Tango", "score": 137, "game_number": 360}),

        # ----------------------------
        # Zip
        # ----------------------------
        ("Zip #20 | 120", {"raw_game": "Zip", "score": 120, "game_number": 20}),
        ("Zip #21 | 2:15 | 3 backtracks", {"raw_game": "Zip", "score": 135, "secondary_metric": 3, "game_number": 21}),
        ("Zip #22 | 0:59 | 1 backtrack", {"raw_game": "Zip", "score": 59, "secondary_metric": 1, "game_number": 22}),
        ("Zip #23 | 45 (2 próby)", {"raw_game": "Zip", "score": 45, "secondary_metric": 2, "game_number": 23}),
        ("Zip #199 | 0:36 🏁\nWith 18 backtracks 🛑\nlnkd.in/zip.",
         {"raw_game": "Zip", "score": 36, "secondary_metric": 18, "game_number": 199}),
    ]
)
def test_parse_post_variations(text, expected):
    result = parse_post(text)
    # Check primary fields
    assert result["raw_game"] == expected["raw_game"]
    assert result["score"] == expected["score"]
    assert result["game_number"] == expected["game_number"]
    # Check secondary metric if present
    if "secondary_metric" in expected:
        assert result["secondary_metric"] == expected["secondary_metric"]
    else:
        assert "secondary_metric" not in result

# ----------------------------
# Unknown / invalid posts
# ----------------------------
@pytest.mark.parametrize(
    "text",
    [
        "This is a LinkedIn post with no game info at all 📝 lnkd.in/xyz",
        "Completely unrelated content",
        ""
    ]
)
def test_unknown_format(text):
    with pytest.raises(ValueError):
        parse_post(text)
