import streamlit as st
import pandas as pd
from utils import aws, data
from constants import PLAYERS, GAMES

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("All Scores")
    items = data.fetch_all(table)
    df_all = pd.DataFrame(items)
    if not df_all.empty:
        df_all["Date"] = df_all["game_date"].apply(lambda x: x.split("_")[1])
        df_all = df_all[["user_id","raw_game","score","metric","Date","timestamp"]]
        df_all = df_all.rename(columns={
            "user_id":"Player",
            "raw_game":"Game",
            "score":"Score",
            "metric":"Metric",
            "timestamp":"Timestamp"
        })
        st.dataframe(df_all, use_container_width=True)
    else:
        st.info("No scores yet.")
