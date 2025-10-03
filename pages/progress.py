import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from constants import PLAYERS, COLORS, GAMES, SCORE_UNITS
from utils import data

def show():
    st.header("Game Progress")

    # Reorder columns: Game | Time Range | Players
    col1, col2, col3 = st.columns([2, 2, 2])
    progress_game = col1.selectbox("Select Game", GAMES, index=0, key="progress_game")
    time_filter = col2.selectbox(
        "Time Range",
        ["All", "Past Year", "Past Month", "Past Week"],
        index=0,
        key="progress_time_filter"
    )
    progress_players = col3.multiselect("Select Players", PLAYERS, default=PLAYERS, key="progress_players")

    # fetch from DynamoDB
    items = data.fetch_all("game_scores")
    if not items:
        st.info("No scores yet.")
        return

    df = pd.DataFrame(items)
    df = df[df["game_name"] == progress_game]
    df = df[df["user_id"].isin(progress_players)]
    if df.empty:
        st.info(f"No data for {progress_game} for selected players.")
        return

    # Ensure game_date is datetime
    df["game_date"] = pd.to_datetime(df["game_date"], format="%d-%m-%Y")

    # Apply time filter
    now = datetime.now()
    if time_filter == "Past Year":
        cutoff = now - timedelta(days=365)
        df = df[df["game_date"] >= cutoff]
    elif time_filter == "Past Month":
        cutoff = now - timedelta(days=30)
        df = df[df["game_date"] >= cutoff]
    elif time_filter == "Past Week":
        cutoff = now - timedelta(days=7)
        df = df[df["game_date"] >= cutoff]

    if df.empty:
        st.info("No data for the selected time range.")
        return

    # Determine max number of scores
    max_scores = df["scores"].apply(lambda x: len(x) if isinstance(x, list) else 0).max()

    # Get unit labels from constants.py
    units_list = SCORE_UNITS.get(progress_game, [])

    # Plot each score as a separate graph
    for idx in range(max_scores):
        y_values = df["scores"].apply(lambda s: s[idx] if isinstance(s, list) and idx < len(s) else None)
        if y_values.isnull().all():
            continue

        unit_label = units_list[idx] if idx < len(units_list) else ""

        # Keep x as datetime for monotonic axis
        df_plot = df.copy()
        df_plot["score_y"] = y_values

        fig = px.line(
            df_plot,
            x="game_date",
            y="score_y",
            color="user_id",
            markers=True,
            line_shape="spline",
            color_discrete_map=COLORS,
            template="plotly_dark"
        )

        # Format x-axis to show only day
        fig.update_xaxes(
            tickformat="%d-%m-%Y",
            dtick="D1",  # one day per tick
            tickangle=45
        )

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate=(
                "Date: %{x|%d-%m-%Y}<br>"
                f"Score: %{{y}}<br>"
                f"Player: %{{color}}<extra></extra>"
            )
        )

        st.subheader(f"Score #{idx+1} ({unit_label})")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
