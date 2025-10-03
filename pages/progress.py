import streamlit as st
import pandas as pd
import plotly.express as px
from constants import PLAYERS, COLORS, GAMES
from utils import data, aws

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG, table_name="game_scores")  
    st.header("Game Progress")

    col1, col2, col3 = st.columns([2, 2, 1])
    progress_game = col1.selectbox("Select Game", GAMES, index=0, key="progress_game")
    progress_players = col2.multiselect("Select Players", PLAYERS, default=PLAYERS, key="progress_players")
    debug_mode = col3.checkbox("Debug Mode", value=False, key="debug_mode")

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

    # Filter to numeric metrics only
    numeric_metrics = []
    if "score" in df.columns:
        numeric_metrics.append("score")
    if "secondary_metric" in df.columns and df["secondary_metric"].notna().any():
        numeric_metrics.append("secondary_metric")

    if not numeric_metrics:
        st.info("No numeric metrics found for plotting.")
        return

    primary_metric = numeric_metrics[0]
    secondary_metric = numeric_metrics[1] if len(numeric_metrics) > 1 else None

    def plot_metric(metric_name):
        fig = px.line(
            df, 
            x="game_number", 
            y=metric_name, 
            color="user_id", 
            markers=True, 
            line_shape="spline",
            color_discrete_map=COLORS, 
            template="plotly_dark"
        )
        fig.update_traces(
            line=dict(width=3), 
            marker=dict(size=8), 
            hovertemplate=f'Game #: %{{x}}<br>{metric_name}: %{{y}}<extra></extra>'
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.subheader(f"Primary Metric: {primary_metric}")
    plot_metric(primary_metric)
    if secondary_metric:
        st.subheader(f"Secondary Metric: {secondary_metric}")
        plot_metric(secondary_metric)

    # Debug mode
    if debug_mode:
        st.subheader("Debug: Data Preview")
        st.dataframe(df[["user_id", "game_number", primary_metric, secondary_metric if secondary_metric else None]].head())
        st.write(f"Total rows: {len(df)} | Unique games: {df['game_number'].nunique()}")