import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from constants import PLAYERS, COLORS, GAMES
from utils import data, aws

def show():
    """
    Display the Progress tab with a clean, theme-aware Plotly line chart.
    """

    # Get DynamoDB table
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("Game Progress")

    # --- Controls ---
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        progress_game = st.selectbox("Select Game", GAMES, index=0, key="progress_game")
    
    # Ensure session_state.progress_players is always a valid list
    if not isinstance(st.session_state.get("progress_players"), list):
        st.session_state.progress_players = PLAYERS.copy()

    with col2:
        progress_players = st.multiselect(
            "Select Players",
            options=PLAYERS,
            default=st.session_state.progress_players,
            key="progress_players"
        )
    
    with col3:
        date_filter = st.selectbox("Date Range", ["Last 7 days", "Last 30 days", "All"], index=0)

    # --- Fetch data ---
    items = data.fetch_all(table)
    if not items:
        st.info("No scores yet.")
        return

    df = pd.DataFrame(items)
    if df.empty:
        st.info("No scores yet.")
        return

    df["Date"] = pd.to_datetime(df["game_date"].apply(lambda x: x.split("_")[1]))
    df = df[df["raw_game"] == progress_game]
    df = df[df["user_id"].isin(progress_players)]

    # Filter by date
    if date_filter == "Last 7 days":
        df = df[df["Date"] >= datetime.utcnow() - timedelta(days=7)]
    elif date_filter == "Last 30 days":
        df = df[df["Date"] >= datetime.utcnow() - timedelta(days=30)]

    if df.empty:
        st.info(f"No data for {progress_game} in selected range for selected players.")
        return

    # --- Theme-aware colors ---
    is_dark = st.get_option("theme.base") == "dark"
    bg_color = "#0e1117" if is_dark else "#ffffff"
    text_color = "#ffffff" if is_dark else "#000000"
    grid_color = "#444444" if is_dark else "#cccccc"

    # --- Plotly line chart ---
    fig = px.line(
        df,
        x="Date",
        y="score",
        color="user_id",
        markers=True,
        line_shape="spline"
    )

    # Customize colors and markers per player
    for player in progress_players:
        fig.update_traces(
            selector=dict(name=player),
            line=dict(color=COLORS.get(player, "#ffffff"), width=4),
            marker=dict(size=8),
            name=player
        )

    # Layout customization for theme integration
    fig.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color),
        xaxis=dict(showgrid=True, gridcolor=grid_color, title=dict(text="Date")),
        yaxis=dict(showgrid=True, gridcolor=grid_color, title=dict(text="Score")),
        legend=dict(title="Player"),
        margin=dict(l=20, r=20, t=40, b=20)
    )

    # Remove Plotly modebar for clean integration
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
