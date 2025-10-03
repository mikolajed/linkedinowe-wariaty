import streamlit as st
from utils import data, parser
from constants import PLAYERS, GAMES
from datetime import datetime

def show():
    st.header("📝 Submit a LinkedIn Game Post")
    
    # Raw post input
    raw_post = st.text_area(
        "Paste LinkedIn post here", 
        key="raw_post_input",
        placeholder="""Eg. Zip #199 | 0:36 🏁\nWith 18 backtracks 🛑\nlnkd.in/zip."""
    )

    # Player selection
    player = st.selectbox("Select Player", PLAYERS, index=0, key="submit_player")

    # Manual mode toggle
    manual_mode = st.checkbox("Manual Input", key="submit_manual")

    # Initialize parsed fields
    parsed = {}
    scores, units = [], []
    game_number, game_date, game = None, None, None

    # Try parsing automatically
    if raw_post.strip():
        try:
            parsed = parser.parse_post(raw_post)
            scores = parsed.get("scores", [])
            units = parsed.get("units", [])
            game_number = parsed.get("game_number")
            game = parsed.get("game_name")
            game_date = parsed.get("game_date")
        except Exception as e:
            st.warning(f"Could not parse post: {e}")

    # Manual input fields
    if manual_mode:
        game = st.selectbox("Select Game", GAMES, index=0 if game is None else GAMES.index(game))
        col1, col2 = st.columns(2)
        scores_input = col1.text_input(
            "Scores (comma-separated)", 
            value=", ".join(str(s) for s in scores),
            placeholder="e.g., 10, 20, 30",
            key="submit_scores"
        )
        units_input = col2.text_input(
            "Units (comma-separated)", 
            value=", ".join(units),
            placeholder="e.g., points, guesses",
            key="submit_units"
        )
        game_number = st.number_input(
            "Game Number", 
            value=game_number or 1, 
            min_value=1,
            key="submit_game_number"
        )
        game_date = st.date_input(
            "Game Date (dd-mm-yyyy)", 
            value=game_date or datetime.today(),
            key="submit_game_date"
        )

        try:
            scores = [int(s.strip()) for s in scores_input.split(",") if s.strip()]
        except ValueError:
            st.warning("Scores must be integers.")
            return
        units = [u.strip() for u in units_input.split(",") if u.strip()]

    # Submit
    if st.button("Submit Post"):
        if not manual_mode:
            post_item = data.save_post(player, raw_post)
            st.success(f"Post submitted for {player} ({game or 'Unknown'}).")
            return

        # Data validation
        if not game or game not in GAMES:
            st.error("Invalid game selected.")
            return
        if not scores:
            st.error("No scores provided.")
            return
        if len(scores) != len(units):
            st.error("Number of scores and units must match.")
            return
        
        data.save_score(
            user_id=player,
            game_name=game,
            game_number=game_number,
            scores=scores,
            units=units,
            game_date=game_date.strftime("%d-%m-%Y") if hasattr(game_date, "strftime") else str(game_date)
        )
        st.success(f"Score submitted for {player} ({game or 'Unknown'}).")

