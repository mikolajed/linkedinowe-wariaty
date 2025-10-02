import streamlit as st
import boto3
import re
from datetime import datetime
import pandas as pd
import os

# Config/Secrets
try:
    AWS_CFG = st.secrets.get("aws", {})
except Exception as e:
    st.error("Missing secrets – add [aws] section in Streamlit Cloud Secrets tab.")
    st.stop()

# AWS DynamoDB (or mock)
def get_ddb_table():
    try:
        if AWS_CFG.get("access_key_id"):
            session = boto3.Session(
                region_name=AWS_CFG.get("region", "us-east-1"),
                aws_access_key_id=AWS_CFG.get("access_key_id"),
                aws_secret_access_key=AWS_CFG.get("secret_access_key"),
            )
            ddb = session.resource("dynamodb")
            return ddb.Table("game-scores")
        else:
            st.warning("No AWS credentials – using in-memory storage (data lost on restart).")
            class MockTable:
                def __init__(self): self.data = []
                def put_item(self, Item): self.data.append(Item)
                def scan(self): return {"Items": self.data}
                def delete_item(self, Key): self.data = [i for i in self.data if not (i.get('user_id') == Key['user_id'] and i.get('game_date') == Key['game_date'])]
            return MockTable()
    except Exception as e:
        st.error(f"DynamoDB error: {str(e)}. Check credentials and table 'game-scores'.")
        st.stop()

table = get_ddb_table()

# Hardcoded Players and Games
PLAYERS = ["Mikuś", "Maciuś", "Patryk"]
GAMES = ["Pinpoint", "Queens", "Crossclimb", "Tango"]

# Parsing Logic
def parse_post(text: str):
    text = text.strip()
    m = re.search(r"Pinpoint #\d+ \|\s*(\d+)\s*guesses", text, re.IGNORECASE)
    if m:
        return {"game": "Pinpoint", "score": int(m.group(1)), "metric": "guesses (lower better)"}
    m = re.search(r"Queens #\d+ \|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        time_str = m.group(1)
        mins, secs = map(int, time_str.split(":"))
        return {"game": "Queens", "score": mins*60 + secs, "metric": "seconds (lower better)"}
    m = re.search(r"Crossclimb #\d+ \|\s*(\d+)\s*clues", text, re.IGNORECASE)
    if m:
        return {"game": "Crossclimb", "score": int(m.group(1)), "metric": "clues (lower better)"}
    m = re.search(r"Tango #\d+ \|\s*(\d+)\s*points", text, re.IGNORECASE)
    if m:
        return {"game": "Tango", "score": int(m.group(1)), "metric": "points (higher better)"}
    raise ValueError("Could not detect a supported game pattern. Supported games: " + ", ".join(GAMES))

# Save to DynamoDB
def save_score(user: str, parsed: dict):
    item = {
        "user_id": user,
        "game_date": f"{parsed['game']}_{datetime.utcnow().date().isoformat()}",
        "score": parsed["score"],
        "metric": parsed["metric"],
        "timestamp": datetime.utcnow().isoformat(),
        "raw_game": parsed["game"],
    }
    table.put_item(Item=item)
    return item

# Fetch all
def fetch_all():
    try:
        return table.scan().get("Items", [])
    except Exception as e:
        st.error(f"Failed to fetch scores: {str(e)}. Check DynamoDB permissions.")
        return []

# UI
st.set_page_config(page_title="LinkedInowe Wariaty", page_icon="🎮")
st.title("🎮 LinkedInowe Wariaty – Game Score Tracker")
st.markdown("Track scores for Mikuś, Maciuś, and Patryk across Pinpoint, Queens, Crossclimb, and more!")

# Test buttons
st.subheader("🔧 DynamoDB Test")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Test Write"):
        test_item = {
            "user_id": "Mikuś",
            "game_date": f"Pinpoint_{datetime.utcnow().date().isoformat()}",
            "score": 3,
            "metric": "guesses (lower better)",
            "timestamp": datetime.utcnow().isoformat(),
            "raw_game": "Pinpoint",
        }
        try:
            table.put_item(Item=test_item)
            st.success("Test write successful!")
        except Exception as e:
            st.error(f"Test write failed: {str(e)}")
with col2:
    if st.button("Test Read"):
        items = fetch_all()
        if items:
            st.success("Test read successful!")
            st.json(items)
        else:
            st.info("Test read: No items yet.")
with col3:
    if st.button("Test Delete"):
        try:
            key = {'user_id': 'Mikuś', 'game_date': f"Pinpoint_{datetime.utcnow().date().isoformat()}"}
            table.delete_item(Key=key)
            st.success("Test delete successful!")
        except Exception as e:
            st.error(f"Test delete failed: {str(e)}")

# Score submission
st.header("📝 Submit a New Score")
user_id = st.selectbox("Select Player", PLAYERS, help="Choose who you are.")
post = st.text_area("Paste the LinkedIn share text here", height=150, placeholder="E.g., Pinpoint #135 | 3 guesses")
if st.button("Save Score", key="save_score"):
    if not post.strip():
        st.error("Please paste a valid game post!")
    else:
        try:
            parsed = parse_post(post)
            saved = save_score(user_id, parsed)
            st.success(f"Saved **{parsed['game']}** – score {parsed['score']} {parsed['metric']}")
            st.json(saved)
        except ValueError as e:
            st.error(str(e))

# All entries with filtering
st.header("📋 All Scores")
with st.form("filter_form"):
    col1, col2 = st.columns(2)
    with col1:
        filter_player = st.selectbox("Filter by Player", ["All"] + PLAYERS, index=0)
    with col2:
        filter_game = st.selectbox("Filter by Game", ["All"] + GAMES, index=0)
    filter_button = st.form_submit_button("Apply Filters")

items = fetch_all()
if filter_player != "All":
    items = [i for i in items if i["user_id"] == filter_player]
if filter_game != "All":
    items = [i for i in items if i["raw_game"] == filter_game]

if items:
    df = pd.DataFrame(items)[["user_id", "raw_game", "score", "metric", "game_date", "timestamp"]]
    df["game_date"] = df["game_date"].apply(lambda x: x.split("_")[1])
    df = df.rename(columns={"user_id": "Player", "raw_game": "Game", "score": "Score", "metric": "Metric", "game_date": "Date", "timestamp": "Timestamp"})
    df = df.sort_values("Timestamp", ascending=False)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No scores match the filters.")