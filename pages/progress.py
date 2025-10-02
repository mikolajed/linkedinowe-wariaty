import streamlit as st
import pandas as pd
import plotly.express as px
from utils import aws, data
from constants import PLAYERS, GAMES, COLORS
from datetime import datetime, timedelta

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("Game Progress")
    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        progress_game = st.selectbox("Select Game", GAMES, index=0, key="progress_game")
    with col2:
        progress_players = st.multiselect("Select Players", PLAYERS, default=PLAYERS, key="progress_players")
    with col3:
        date_filter = st.selectbox("Date Range", ["Last 7 days","Last 30 days","All"], index=0)

    items = data.fetch_all(table)
    df = pd.DataFrame(items)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["game_date"].apply(lambda x: x.split("_")[1]))
        df = df[df["raw_game"]==progress_game]
        if date_filter=="Last 7 days":
            df = df[df["Date"] >= datetime.utcnow() - timedelta(days=7)]
        elif date_filter=="Last 30 days":
            df = df[df["Date"] >= datetime.utcnow() - timedelta(days=30)]
        df = df[df["user_id"].isin(progress_players)]

        if df.empty:
            st.info(f"No data for {progress_game} for selected players.")
            return

        fig = px.line(df, x="Date", y="score", color="user_id", markers=True, line_shape="spline")
        for user in progress_players:
            fig.update_traces(selector=dict(name=user), line=dict(color=COLORS.get(user, "#fff"), width=4), marker=dict(size=8))
        fig.update_layout(
            title=f"{progress_game} Progress",
            xaxis_title="Date",
            yaxis_title="Score",
            plot_bgcolor="#1f1f1f",
            paper_bgcolor="#1f1f1f",
            font=dict(color="#fff"),
            legend_title="Player"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet.")
