import streamlit as st
import pandas as pd
import plotly.express as px
from constants import PLAYERS, COLORS, GAMES
from utils import data, aws

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG, table_name="game_scores")
    st.header("Game Progress")

    col1, col2 = st.columns([2, 2])
    progress_game = col1.selectbox("Select Game", GAMES, index=0, key="progress_game")
    if not isinstance(st.session_state.get("progress_players"), list):
        st.session_state.progress_players = PLAYERS.copy()
    progress_players = col2.multiselect("Select Players", PLAYERS, default=st.session_state.progress_players, key="progress_players")

    items = data.fetch_all(table)
    if not items:
        st.info("No scores yet.")
        return

    df = pd.DataFrame(items)
    df = df[df["raw_game"] == progress_game]
    df = df[df["user_id"].isin(progress_players)]
    if df.empty:
        st.info(f"No data for {progress_game} for selected players.")
        return

    metrics = [c for c in df.columns if c not in ["user_id", "raw_game", "game_number", "game_date", "timestamp"]]
    primary_metric = metrics[0]
    secondary_metric = metrics[1] if len(metrics) > 1 else None

    def plot_metric(metric_name):
        fig = px.line(df, x="game_number", y=metric_name, color="user_id", markers=True, line_shape="spline",
                      color_discrete_map=COLORS, template="plotly_white")
        fig.update_traces(line=dict(width=3), marker=dict(size=8), hovertemplate=f'Game #: %{{x}}<br>{metric_name}: %{{y}}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, theme=None)

    st.subheader(f"Primary Metric: {primary_metric}")
    plot_metric(primary_metric)
    if secondary_metric:
        st.subheader(f"Secondary Metric: {secondary_metric}")
        plot_metric(secondary_metric)
