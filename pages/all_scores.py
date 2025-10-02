import streamlit as st
import pandas as pd
from utils import aws, data
from constants import PLAYERS, GAMES

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)
    st.header("All Scores")

    items = data.fetch_all(table)
    if not items:
        st.info("No scores yet.")
        return

    df_all = pd.DataFrame(items)
    df_all = df_all[["user_id","raw_game","game_number","score","metric","timestamp"]]
    df_all = df_all.rename(columns={
        "user_id":"Player",
        "raw_game":"Game",
        "game_number":"Game Number",
        "score":"Score",
        "metric":"Metric",
        "timestamp":"Timestamp"
    })

    # --- Filters ---
    col1, col2 = st.columns([2,2])
    with col1:
        selected_game = st.selectbox("Filter by Game", options=["All"] + GAMES, index=0)
    with col2:
        selected_players = st.multiselect("Filter by Player", options=PLAYERS, default=PLAYERS)

    if selected_game != "All":
        df_all = df_all[df_all["Game"] == selected_game]
    if selected_players:
        df_all = df_all[df_all["Player"].isin(selected_players)]
    else:
        st.warning("No players selected. Showing empty table.")
        df_all = pd.DataFrame(columns=df_all.columns)

    df_all = df_all.sort_values(by=["Game", "Game Number"])
    st.dataframe(df_all, use_container_width=True)
