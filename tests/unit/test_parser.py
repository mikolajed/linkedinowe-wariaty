import pytest
from utils.parser import parse_post

@pytest.mark.parametrize(
    "text, expected",
    [
        # Mini Sudoku
        ("Mini Sudoku #123 | 2:45", {"game_name": "Mini Sudoku", "game_number": 123, "scores": [165]}),
        ("Mini Sudoku #42 | 0:59", {"game_name": "Mini Sudoku", "game_number": 42, "scores": [59]}),
        ("Mini Sudoku #77 | 1:02:03", {"game_name": "Mini Sudoku", "game_number": 77, "scores": [3723]}),
        ("Mini Sudoku #52 | 6:29 and flawless ✏️\nThe classic game.\nlnkd.in/minisudoku.",
         {"game_name": "Mini Sudoku", "game_number": 52, "scores": [389]}),

        # Pinpoint
        ("Pinpoint #42 | 5 guesses", {"game_name": "Pinpoint", "game_number": 42, "scores": [5]}),
        ("Pinpoint #43 | 1 guess", {"game_name": "Pinpoint", "game_number": 43, "scores": [1]}),
        ("Pinpoint #100 | 3 guesses | 95% accuracy", {"game_name": "Pinpoint", "game_number": 100, "scores": [3, 95]}),
        ("Pinpoint #101 | 4 próby | 88%", {"game_name": "Pinpoint", "game_number": 101, "scores": [4, 88]}),
        ("Pinpoint #520 | 1 guess\n1️⃣ | 100% match 📌\nlnkd.in/pinpoint.",
         {"game_name": "Pinpoint", "game_number": 520, "scores": [1, 100]}),

        # Queens
        ("Queens #10 | 1:30", {"game_name": "Queens", "game_number": 10, "scores": [90]}),
        ("Queens #11 | 12:05", {"game_name": "Queens", "game_number": 11, "scores": [725]}),
        ("Queens #520 | 1:57\nFirst 👑s: 🟦 🟩 🟫\nlnkd.in/queens.",
         {"game_name": "Queens", "game_number": 520, "scores": [117]}),

        # Crossclimb
        ("Crossclimb #15 | 8", {"game_name": "Crossclimb", "game_number": 15, "scores": [8]}),
        ("Crossclimb #16 | 8:12", {"game_name": "Crossclimb", "game_number": 16, "scores": [492]}),
        ("Crossclimb #520 | 3:13\nFill order: 1️⃣ 2️⃣ 3️⃣ 5️⃣ 4️⃣ 🔼 🔽 🪜\nlnkd.in/crossclimb.",
         {"game_name": "Crossclimb", "game_number": 520, "scores": [193]}),

        # Tango
        ("Tango #5 | 45", {"game_name": "Tango", "game_number": 5, "scores": [45]}),
        ("Tango #6 | 1:30", {"game_name": "Tango", "game_number": 6, "scores": [90]}),
        ("Tango #7 | 1:02:03", {"game_name": "Tango", "game_number": 7, "scores": [3723]}),
        ("Tango #360 | 2:17 and flawless\nFirst 5 placements:\nlnkd.in/tango.",
         {"game_name": "Tango", "game_number": 360, "scores": [137]}),

        # Zip
        ("Zip #20 | 120", {"game_name": "Zip", "game_number": 20, "scores": [120]}),
        ("Zip #21 | 2:15 | 3 backtracks", {"game_name": "Zip", "game_number": 21, "scores": [135, 3]}),
        ("Zip #22 | 0:59 | 1 backtrack", {"game_name": "Zip", "game_number": 22, "scores": [59, 1]}),
        ("Zip #23 | 45 (2 próby)", {"game_name": "Zip", "game_number": 23, "scores": [45, 2]}),
        ("Zip #199 | 0:36 🏁\nWith 18 backtracks 🛑\nlnkd.in/zip.",
         {"game_name": "Zip", "game_number": 199, "scores": [36, 18]}),
    ]
)
def test_parse_post_variations(text, expected):
    result = parse_post(text)
    assert result["game_name"] == expected["game_name"]
    assert result["game_number"] == expected["game_number"]
    assert result["scores"] == expected["scores"]

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
