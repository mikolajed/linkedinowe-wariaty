import streamlit as st
from utils import parser, data, aws
from constants import PLAYERS
from datetime import datetime

def show():
    AWS_CFG = st.secrets.get("aws", {})

    scores_table = aws.get_ddb_table(AWS_CFG, "game_scores") 
    raw_table = aws.get_ddb_table(AWS_CFG, "raw_game_posts") 

    st.header("Submit a New Score")
    user_id = st.selectbox("Select Player", PLAYERS, key="submit_player")
    post = st.text_area("Paste the LinkedIn share text here", height=150)

    debug_mode = st.checkbox("Debug Mode", value=False, key="debug_mode")

    if st.button("Save Score", key="save_score"):
        if not post.strip():
            st.error("Please paste a valid game post!")
            return

        timestamp = datetime.utcnow().isoformat()

        raw_table.put_item(Item={"user_id": user_id, "timestamp": timestamp, "raw_post": post})

        try:
            parsed = parser.parse_post(post)
            saved = data.save_score(scores_table, user_id, parsed)
            st.success(f"Saved **{parsed['raw_game']}** – score {parsed['score']} {parsed['metric']}")
            if debug_mode:
                st.subheader("Debug: Raw Saved Item")
                st.json(saved)
        except ValueError as e:
            st.error(str(e))