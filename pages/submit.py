import streamlit as st
from utils import data, parser
from constants import PLAYERS, GAMES, SCORE_UNITS
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

    # Initialize parsed fields
    parsed = {}
    scores, parsed_units = [], []
    game_number, game_date, parsed_game = None, None, None

    # Try parsing automatically
    if raw_post.strip():
        try:
            parsed = parser.parse_post(raw_post)
            scores = parsed.get("scores", [])
            parsed_units = parsed.get("units", [])
            game_number = parsed.get("game_number")
            parsed_game = parsed.get("game_name")
            game_date = parsed.get("game_date")

            if not parsed_units and parsed_game in SCORE_UNITS:
                parsed_units = SCORE_UNITS[parsed_game]

        except Exception as e:
            st.warning(f"Could not parse post: {e}")

    # Only show advanced modify if parsed game exists
    show_advanced = parsed_game is not None and raw_post.strip()
    if show_advanced:
        advanced_modify = st.checkbox("Advanced Modify", value=False, key="advanced_modify")

        if advanced_modify:
            # Initialize session_state if first run
            if "previous_game" not in st.session_state:
                st.session_state.previous_game = parsed_game

            # Determine default index
            default_index = GAMES.index(parsed_game) if parsed_game in GAMES else 0
            game = st.selectbox("Select Game", GAMES, index=default_index, key="advanced_game_select")

            # Determine units: update if game changed OR first render
            if st.session_state.previous_game != game:
                st.session_state.previous_game = game
                current_units = SCORE_UNITS.get(game, [])
            else:
                current_units = parsed_units if parsed_units else SCORE_UNITS.get(game, [])

            col1, col2 = st.columns(2)
            scores_input = col1.text_input(
                "Scores (comma-separated)", 
                value=", ".join(str(s) for s in scores),
                placeholder="e.g., 10, 20, 30",
                key="submit_scores"
            )

            units_input = col2.text_input(
                "Units (comma-separated)", 
                value=", ".join(current_units),
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

            # Parse scores and units
            try:
                scores = [int(s.strip()) for s in scores_input.split(",") if s.strip()]
            except ValueError:
                st.warning("Scores must be integers.")
                return
            units = [u.strip() for u in units_input.split(",") if u.strip()]

    # Submit button
    if st.button("Submit Post"):
        if not show_advanced or not advanced_modify:
            data.save_post(player, raw_post)
            st.success(f"Post submitted for {player} ({parsed_game or 'Unknown'}).")
            return

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
        st.success(f"Score submitted for {player} ({game}).")
