import streamlit as st
from utils import aws, data
from constants import PLAYERS, GAMES

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("Debug / Test Data")

    col1, col2 = st.columns([2,2])
    with col1:
        test_player = st.selectbox("Select Player", PLAYERS, key="test_player")
    with col2:
        test_game = st.selectbox("Select Game", GAMES, key="test_game")

    days = st.slider("Number of entries", 1, 30, 7)

    if st.button("Add Test Data"):
        data.generate_test_data(table, test_player, game=test_game, days=days)
        st.success(f"Added {days} entries for {test_player} ({test_game})!")

    st.checkbox("Debug Mode", value=st.session_state.get("debug_mode", False), key="debug_mode")
