import streamlit as st
import pandas as pd
from utils import data
from constants import PLAYERS

def show():
    st.header("Posts")

    items = data.fetch_all("raw_game_posts")

    if not items:
        st.info("No posts yet.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(items)

    # Parse timestamp for sorting
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values(by="timestamp", ascending=False)

    # Filter only allowed players
    df = df[df["user_id"].isin(PLAYERS)]

    # Columns to display (no scores)
    df_display = df[["user_id", "raw_post", "timestamp"]].rename(columns={
        "user_id": "Player",
        "raw_post": "Post",
        "timestamp": "Submitted At"
    })

    st.dataframe(df_display, use_container_width=True)
