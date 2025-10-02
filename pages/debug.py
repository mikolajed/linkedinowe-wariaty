import streamlit as st
from utils import aws, data
from constants import PLAYERS, GAMES

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("Debug / Test Data")

    # Controls for test data generation
    col1, col2, col3 = st.columns(3)
    with col1:
        test_player = st.selectbox("Select Player", PLAYERS, key="test_player")
    with col2:
        test_game = st.selectbox("Select Game", GAMES, index=GAMES.index("Mini Sudoku") if "Mini Sudoku" in GAMES else 0, key="test_game")
    with col3:
        num_days = st.number_input("Days of Data", min_value=1, max_value=60, value=7, step=1, key="test_days")

    if st.button("Add Test Data"):
        data.generate_test_data(table, test_player, game=test_game, days=num_days)
        st.success(f"Added {num_days} days of test data for {test_player} in {test_game}!")

    st.checkbox("Debug Mode", value=st.session_state.get("debug_mode", False), key="debug_mode")
