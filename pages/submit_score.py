import streamlit as st
from utils import parser, data, aws
from constants import PLAYERS

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("Submit a New Score")
    user_id = st.selectbox("Select Player", PLAYERS, key="submit_player")
    post = st.text_area("Paste the LinkedIn share text here", height=150, placeholder="E.g., Pinpoint #135 | 3 guesses")

    if st.button("Save Score", key="save_score"):
        if not post.strip():
            st.error("Please paste a valid game post!")
        else:
            try:
                parsed = parser.parse_post(post)
                saved = data.save_score(table, user_id, parsed)
                st.success(f"Saved **{parsed['game']}** – score {parsed['score']} {parsed['metric']}")
                st.json(saved)
            except ValueError as e:
                st.error(str(e))
