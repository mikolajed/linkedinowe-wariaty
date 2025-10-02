import streamlit as st
import pandas as pd
import plotly.express as px
from constants import PLAYERS, COLORS, GAMES
from utils import data, aws

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG, table_name="game_scores")
    st.header("Game Progress")

    # --- Controls ---
    col1, col2 = st.columns([2, 2])
    with col1:
        progress_game = st.selectbox("Select Game", GAMES, index=0, key="progress_game")
    if not isinstance(st.session_state.get("progress_players"), list):
        st.session_state.progress_players = PLAYERS.copy()
    with col2:
        progress_players = st.multiselect("Select Players", PLAYERS,
                                          default=st.session_state.progress_players,
                                          key="progress_players")

    # --- Fetch data ---
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

    # --- Detect numeric columns (primary & secondary metrics) ---
    metrics = [c for c in df.columns if c not in ["user_id", "raw_game", "game_number", "game_date", "timestamp"]]
    if not metrics:
        st.warning("No numeric metrics found for this game.")
        return

    primary_metric = metrics[0]
    secondary_metric = metrics[1] if len(metrics) > 1 else None

    def plot_metric(metric_name):
        fig = px.line(
            df,
            x="game_number",
            y=metric_name,
            color="user_id",
            markers=True,
            line_shape="spline",
            color_discrete_map=COLORS,
            template="plotly_white"
        )
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate=f'Game #: %{{x}}<br>{metric_name}: %{{y}}<extra></extra>'
        )
        is_dark = st.get_option("theme.base") == "dark"
        bg_color = 'rgba(0,0,0,0.9)' if is_dark else 'rgba(255,255,255,0.95)'
        grid_color = 'rgba(255,255,255,0.1)' if is_dark else 'rgba(0,0,0,0.1)'
        text_color = '#FFFFFF' if is_dark else '#000000'
        legend_text_color = '#FFFFFF' if is_dark else '#000000'
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor=grid_color, title="Game #"),
            yaxis=dict(showgrid=True, gridcolor=grid_color, title=metric_name),
            legend=dict(
                title=dict(text="Player", font=dict(color=legend_text_color)),
                font=dict(color=legend_text_color),
                bgcolor=bg_color,
                bordercolor=grid_color,
                borderwidth=1,
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            hovermode='x unified',
            hoverlabel=dict(bgcolor=bg_color, font_color=text_color)
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, theme=None)

    st.subheader(f"Primary Metric: {primary_metric}")
    plot_metric(primary_metric)

    if secondary_metric:
        st.subheader(f"Secondary Metric: {secondary_metric}")
        plot_metric(secondary_metric)
