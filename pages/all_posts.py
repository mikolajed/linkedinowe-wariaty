import streamlit as st
import pandas as pd
from utils import aws, data

def show():
    """
    Display all raw LinkedIn game posts in chronological order (latest first)
    """
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG, table_name="raw_game_posts")

    st.header("All Raw Posts")

    items = data.fetch_all(table)
    if not items:
        st.info("No posts yet.")
        return

    df = pd.DataFrame(items)
    if df.empty:
        st.info("No posts yet.")
        return

    # Sort by timestamp descending
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by="timestamp", ascending=False)

    # Show selected columns
    df_display = df[["user_id", "raw_post", "timestamp"]].rename(columns={
        "user_id": "Player",
        "raw_post": "Post",
        "timestamp": "Submitted At"
    })

    st.dataframe(df_display, use_container_width=True)
