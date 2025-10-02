import streamlit as st
from utils import parser, data, aws
from constants import PLAYERS
from datetime import datetime

def show():
    AWS_CFG = st.secrets.get("aws", {})

    # Processed scores table
    scores_table = aws.get_ddb_table(AWS_CFG, table_name="game_scores")
    # Raw posts table
    raw_table = aws.get_ddb_table(AWS_CFG, table_name="raw_game_posts")

    st.header("Submit a New Score")
    user_id = st.selectbox("Select Player", PLAYERS, key="submit_player")
    post = st.text_area(
        "Paste the LinkedIn share text here",
        height=150,
        placeholder="E.g., Mini Sudoku #52 | 6:29 and flawless ✏️"
    )

    if st.button("Save Score", key="save_score"):
        if not post.strip():
            st.error("Please paste a valid game post!")
            return

        timestamp = datetime.utcnow().isoformat()

        # Save raw post
        raw_item = {
            "user_id": user_id,
            "timestamp": timestamp,
            "post": post
        }
        raw_table.put_item(Item=raw_item)

        # Parse and save processed score
        try:
            parsed = parser.parse_post(post)
            saved = data.save_score(scores_table, user_id, parsed)
            st.success(f"Saved **{parsed['raw_game']}** – score {parsed['score']} {parsed['metric']}")
            if st.session_state.get("debug_mode", False):
                st.subheader("Debug: Raw Saved Item")
                st.json(saved)
        except ValueError as e:
            st.error(str(e))
