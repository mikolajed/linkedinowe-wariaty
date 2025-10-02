import streamlit as st
import pandas as pd
from datetime import datetime
from utils import aws, data
from constants import PLAYERS, GAMES

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("All Scores")
    
    # Fetch and prepare data
    items = data.fetch_all(table)
    if not items:
        st.info("No scores found.")
        return
        
    df_all = pd.DataFrame(items)
    
    # Process and clean data
    df_all["Date"] = pd.to_datetime(df_all["game_date"].apply(lambda x: x.split("_")[1]))
    df_all["Timestamp"] = pd.to_datetime(df_all["timestamp"])
    df_all = df_all.rename(columns={
        "user_id": "Player",
        "raw_game": "Game",
        "score": "Score",
        "metric": "Metric"
    })
    
    # Convert score to numeric, handle potential conversion errors
    df_all["Score"] = pd.to_numeric(df_all["Score"], errors='coerce')
    df_all = df_all.dropna(subset=["Score"])
    
    # Sidebar filters
    with st.sidebar:
        st.subheader("Filters")
        
        # Game filter
        selected_games = st.multiselect(
            "Select Games",
            options=GAMES,
            default=GAMES,
            key="games_filter"
        )
        
        # Player filter
        selected_players = st.multiselect(
            "Select Players",
            options=PLAYERS,
            default=PLAYERS,
            key="players_filter"
        )
        
        # Date range filter
        date_range = st.date_input(
            "Date Range",
            value=(
                df_all["Date"].min().date(),
                df_all["Date"].max().date()
            ),
            min_value=df_all["Date"].min().date(),
            max_value=df_all["Date"].max().date()
        )
        
        # Best scores only toggle
        show_best_only = st.checkbox(
            "Show best scores only",
            value=True,
            help="When enabled, shows only the best score per player per game per day"
        )
    
    # Apply filters
    filtered_df = df_all[
        (df_all["Game"].isin(selected_games)) &
        (df_all["Player"].isin(selected_players)) &
        (df_all["Date"].dt.date >= date_range[0]) &
        (df_all["Date"].dt.date <= (date_range[1] if len(date_range) > 1 else date_range[0]))
    ]
    
    # Apply best scores filter if enabled
    if show_best_only and not filtered_df.empty:
        # For each player and game and date, keep only their best score
        filtered_df = filtered_df.loc[
            filtered_df.groupby(["Player", "Game", filtered_df["Date"].dt.date])["Score"].idxmax()
        ]
    
    # Sort by date (newest first) and then by player name
    filtered_df = filtered_df.sort_values(by=["Date", "Player"], ascending=[False, True])
    
    # Display metrics
    if not filtered_df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Games Played", len(filtered_df))
        with col2:
            st.metric("Unique Players", filtered_df["Player"].nunique())
        with col3:
            st.metric("Games Tracked", filtered_df["Game"].nunique())
        
        # Add a small gap
        st.write("")
        
        # Display the data in a more readable format
        filtered_display = filtered_df[["Date", "Player", "Game", "Score", "Metric", "Timestamp"]]
        
        # Format the timestamp for better readability
        filtered_display["Timestamp"] = filtered_display["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")
        
        # Display the table with better formatting
        st.dataframe(
            filtered_display,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Date": st.column_config.DateColumn("Date"),
                "Player": "Player",
                "Game": "Game",
                "Score": st.column_config.NumberColumn("Score"),
                "Metric": "Metric",
                "Timestamp": "Recorded At"
            }
        )
        
        # Add download button
        csv = filtered_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f'scores_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
    else:
        st.warning("No scores match the selected filters.")
