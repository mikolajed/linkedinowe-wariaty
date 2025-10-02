import streamlit as st
import pandas as pd
from utils import aws, data
from constants import PLAYERS, GAMES

def show():
    # --- DynamoDB table ---
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("All Scores")

    # --- Fetch data ---
    items = data.fetch_all(table)
    if not items:
        st.info("No scores yet.")
        return

    df_all = pd.DataFrame(items)
    df_all["Date"] = df_all["game_date"].apply(lambda x: x.split("_")[1])
    df_all = df_all[["user_id","raw_game","score","metric","Date","timestamp"]]
    df_all = df_all.rename(columns={
        "user_id":"Player",
        "raw_game":"Game",
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

    # Apply filters
    if selected_game != "All":
        df_all = df_all[df_all["Game"] == selected_game]
    if selected_players:
        df_all = df_all[df_all["Player"].isin(selected_players)]
    else:
        st.warning("No players selected. Showing empty table.")
        df_all = df_all.iloc[0:0]  # Empty dataframe

    # Show dataframe
    st.dataframe(df_all, use_container_width=True)
