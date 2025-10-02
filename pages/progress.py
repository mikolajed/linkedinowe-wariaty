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
    # --- DynamoDB table ---
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("Game Progress")

    # --- Controls ---
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        progress_game = st.selectbox("Select Game", GAMES, index=0, key="progress_game")

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

    # --- Apply date filter ---
    today = datetime.utcnow().date()
    if date_filter == "Last 7 days":
        df = df[df["Date"].dt.date >= today - timedelta(days=7)]
    elif date_filter == "Last 30 days":
        df = df[df["Date"].dt.date >= today - timedelta(days=30)]

    if df.empty:
        st.info(f"No data for {progress_game} in selected range for selected players.")
        return

    # --- Plotly chart ---
    fig = px.line(
        df,
        x="Date",
        y="score",
        color="user_id",
        markers=True,
        line_shape="spline",
        color_discrete_map=COLORS
    )

    # Update line and marker styles
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )

    # Layout customization
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, title="Date"),
        yaxis=dict(showgrid=True, title="Score"),
        legend=dict(title="Player"),
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode='x unified'
    )

    # Display the chart with theme support
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        theme=None  # Use Streamlit's theme
    )
