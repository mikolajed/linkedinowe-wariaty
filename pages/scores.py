import streamlit as st
import pandas as pd
from utils import data
from constants import PLAYERS, GAMES

def show():
    st.header("All Scores")

    # Fetch all scores from DynamoDB (game_scores table)
    items = data.fetch_all("game_scores")
    if not items:
        st.info("No scores yet.")
        return

    df_all = pd.DataFrame(items)
    if df_all.empty:
        st.info("No scores yet.")
        return

    # Filter only allowed players
    df_all = df_all[df_all["user_id"].isin(PLAYERS)]

    # Convert scores + units to a display string
    def format_scores_units(row):
        scores = row.get("scores", [])
        units = row.get("units", [])
        return ", ".join(f"{s} {u}" for s, u in zip(scores, units) if s is not None and u is not None)

    df_all["Scores"] = df_all.apply(format_scores_units, axis=1)

    # Select relevant columns for display
    df_all = df_all[["user_id", "game_name", "game_number", "Scores", "game_date", "timestamp"]].rename(
        columns={
            "user_id": "Player",
            "game_name": "Game",
            "game_number": "Game Number",
            "game_date": "Game Date",
            "timestamp": "Timestamp"
        }
    )

    # Filters
    col1, col2 = st.columns([2, 2])
    selected_game = col1.selectbox("Filter by Game", ["All"] + GAMES)
    selected_players = col2.multiselect("Filter by Player", PLAYERS, default=PLAYERS)

    if selected_game != "All":
        df_all = df_all[df_all["Game"] == selected_game]
    if selected_players:
        df_all = df_all[df_all["Player"].isin(selected_players)]
    else:
        df_all = pd.DataFrame(columns=df_all.columns)

    # Sort nicely
    df_all = df_all.sort_values(by=["Game", "Game Number", "Player"])
    st.dataframe(df_all, use_container_width=True)
