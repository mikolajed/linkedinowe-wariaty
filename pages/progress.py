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
        color_discrete_map=COLORS,
        template='plotly_white'  # Start with a clean template
    )

    # Update line and marker styles
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8),
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Score: %{y}<extra></extra>'
    )

    # Get theme colors from Streamlit
    is_dark = st.get_option("theme.base") == "dark"
    bg_color = 'rgba(0,0,0,0.9)' if is_dark else 'rgba(255,255,255,0.95)'
    grid_color = 'rgba(255,255,255,0.1)' if is_dark else 'rgba(0,0,0,0.1)'
    text_color = '#FFFFFF' if is_dark else '#000000'
    legend_text_color = '#FFFFFF' if is_dark else '#000000'  # Explicit legend text color

    # Layout customization
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            title="Date",
            tickformat='%b %d',  # Format as 'Oct 02'
            tickangle=-45,       # Angle the dates for better readability
            gridcolor=grid_color,
            title_standoff=20,   # Add space between axis and title
            showline=True,
            linecolor=grid_color,
            ticks='outside'
        ),
        yaxis=dict(
            showgrid=True,
            title="Score",
            gridcolor=grid_color,
            title_standoff=20,   # Add space between axis and title
            showline=True,
            linecolor=grid_color,
            ticks='outside'
        ),
        legend=dict(
            title=dict(
                text="Player",
                font=dict(
                    color=legend_text_color,
                    size=12
                )
            ),
            font=dict(
                color=legend_text_color,
                size=11
            ),
            bgcolor=bg_color,
            bordercolor=grid_color,
            borderwidth=1,
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            itemsizing='constant'
        ),
        margin=dict(l=60, r=20, t=40, b=80),  # Increased left and bottom margins
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor=bg_color,
            font_size=12,
            font_color=text_color
        )
    )

    # Display the chart with theme support
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        theme=None  # Use Streamlit's theme
    )
