import streamlit as st
from utils import aws, data
from constants import PLAYERS, GAMES

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG, table_name="game_scores")

    st.header("Debug / Test Data")

    col1, col2 = st.columns([2,2])
    with col1:
        test_player = st.selectbox("Select Player", PLAYERS, key="test_player")
    with col2:
        test_game = st.selectbox("Select Game", GAMES, key="test_game")

    days = st.slider("Number of entries", 1, 30, 7)

    if st.button("Add Test Data"):
        added = data.generate_test_data(table, test_player, game=test_game, days=days)
        st.success(f"Added {len(added)} entries for {test_player} ({test_game})!")
        st.subheader("Last entries:")
        st.dataframe(added, use_container_width=True)

    # Debug Mode toggle
    debug_mode = st.checkbox("Debug Mode", value=st.session_state.get("debug_mode", False))
    st.session_state.debug_mode = debug_mode
