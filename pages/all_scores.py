import streamlit as st
import pandas as pd
from utils import aws, data
from constants import PLAYERS, GAMES

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG, table_name="game-scores")  # Fixed: hyphen
    st.header("All Scores")

    items = data.fetch_all(table)
    if not items:
        st.info("No scores yet.")
        return

    df_all = pd.DataFrame(items)
    if df_all.empty:
        st.info("No scores yet.")
        return

    df_all = df_all[["user_id", "raw_game", "game_number", "score", "secondary_metric", "metric", "timestamp"]]
    df_all = df_all.rename(columns={
        "user_id": "Player",
        "raw_game": "Game",
        "game_number": "Game Number",
        "score": "Score",
        "secondary_metric": "Secondary Metric",
        "metric": "Metric",
        "timestamp": "Timestamp"
    })

    col1, col2 = st.columns([2, 2])
    selected_game = col1.selectbox("Filter by Game", ["All"] + GAMES)
    selected_players = col2.multiselect("Filter by Player", PLAYERS, default=PLAYERS)

    if selected_game != "All":
        df_all = df_all[df_all["Game"] == selected_game]
    if selected_players:
        df_all = df_all[df_all["Player"].isin(selected_players)]
    else:
        df_all = pd.DataFrame(columns=df_all.columns)

    df_all = df_all.sort_values(by=["Game", "Game Number"])
    st.dataframe(df_all, use_container_width=True)