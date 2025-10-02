import streamlit as st
from utils import parser, data, aws
from constants import PLAYERS

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("Submit a New Score")
    user_id = st.selectbox("Select Player", PLAYERS, key="submit_player")
    post = st.text_area(
        "Paste the LinkedIn share text here", 
        height=150, 
        placeholder="""E.g., Mini Sudoku #52 | 6:29 and flawless ✏️ The classic game, made mini. Handcrafted by the originators of "Sudoku." lnkd.in/minisudoku."""
    )

    if st.button("Save Score", key="save_score"):
        if not post.strip():
            st.error("Please paste a valid game post!")
        else:
            try:
                parsed = parser.parse_post(post)
                saved = data.save_score(table, user_id, parsed)

                st.success(f"Saved **{parsed['game']}** – score {parsed['score']} {parsed['metric']}")

                # Only show JSON when Debug Mode is active
                if st.session_state.get("debug_mode", False):
                    st.subheader("Debug: Raw Saved Item")
                    st.json(saved)

            except ValueError as e:
                st.error(str(e))
