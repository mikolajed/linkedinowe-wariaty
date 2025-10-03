import streamlit as st
from utils import aws, data
from constants import PLAYERS, GAMES

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)
    st.header("⚙️ Debug / Test Data")

    debug_mode = st.checkbox("Enable Debug Mode", value=st.session_state.get("debug_mode", False), key="debug_mode")
    include_pysiek = st.checkbox("Include Pysiek?", value=True)

    col1, col2 = st.columns([2,2])
    test_player = col1.selectbox("Select Player", PLAYERS, key="test_player")
    test_game = col2.selectbox("Select Game", GAMES, key="test_game")

    entry_range = st.select_slider("Select entry range", options=list(range(1, 367)), value=(1,7))
    start_entry, end_entry = entry_range

    if st.button("Add Test Data"):
        players_to_use = PLAYERS.copy()
        if not include_pysiek and "Pysiek" in players_to_use:
            players_to_use.remove("Pysiek")

        success = data.generate_test_data(
            table,
            test_player,
            game=test_game,
            start_day=start_entry,
            end_day=end_entry,
            extra_players=players_to_use
        )
        if success:
            st.success(f"Added entries {start_entry} → {end_entry} for {test_player} for game: {test_game}")
            if debug_mode:
                st.info(f"Debug Info: Players included = {', '.join(players_to_use)}")
        else:
            st.error("Failed to add test data. Check DynamoDB permissions.")