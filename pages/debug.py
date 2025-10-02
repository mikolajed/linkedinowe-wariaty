import streamlit as st
from utils import aws, data
from constants import PLAYERS, GAMES

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("⚙️ Debug / Test Data")

    st.subheader("Generate Test Scores")

    # --- Player and Game selection ---
    col1, col2 = st.columns(2)
    with col1:
        test_player = st.selectbox("Select Main Player", PLAYERS, key="test_player")
    with col2:
        test_game = st.selectbox("Select Game", GAMES, key="test_game")

    # --- Additional options ---
    st.subheader("Options")
    days = st.slider("Number of entries to generate", 1, 30, 7)
    include_pysiek = st.checkbox("Include Pysiek in test data?", value=True)
    debug_mode = st.checkbox("Enable Debug Mode", value=st.session_state.get("debug_mode", False), key="debug_mode")

    # --- Generate button ---
    if st.button("Add Test Data"):
        players_to_use = PLAYERS.copy()
        if not include_pysiek and "Pysiek" in players_to_use:
            players_to_use.remove("Pysiek")
        data.generate_test_data(
            table, 
            test_player, 
            game=test_game, 
            days=days, 
            extra_players=players_to_use
        )
        st.success(f"Added {days} entries for {test_player} ({test_game})!")
        if debug_mode:
            st.info(f"Test data will include: {', '.join(players_to_use)}")
