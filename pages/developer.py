import streamlit as st
from datetime import datetime, timedelta
from utils import data
from constants import PLAYERS, GAMES

def show():
    st.header("🛠️ Developer / Test Data")

    # Player and game selection
    col1, col2 = st.columns([2, 2])
    test_player = col1.selectbox("Select Player", PLAYERS, key="dev_player")
    test_game = col2.selectbox("Select Game", GAMES, key="dev_game")

    # Two date pickers
    today = datetime.today().date()
    default_start = today - timedelta(days=6)  # default: past 7 days
    default_end = today

    start_date = st.date_input("Start Date", value=default_start, key="dev_start_date")
    end_date = st.date_input("End Date", value=default_end, key="dev_end_date")

    if start_date > end_date:
        st.warning("Start date cannot be after end date.")
        return

    if st.button("Add Test Data"):
        try:
            # Generate entries for the date range
            data.generate_test_data(
                user=test_player,
                game=test_game,
                start_date=start_date,
                end_date=end_date
            )

            num_entries = (end_date - start_date).days + 1
            st.success(
                f"Added {num_entries} entries for {test_player} "
                f"for game: {test_game} from {start_date} to {end_date}"
            )

        except Exception as e:
            st.error(f"Error generating data for {test_player}: {e}")
