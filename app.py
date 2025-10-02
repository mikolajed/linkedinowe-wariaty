import streamlit as st
import boto3
import re
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
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
    return table.scan().get("Items", [])

# Leaderboard
def leaderboard(game: str):
    items = [i for i in fetch_all() if i["raw_game"].lower() == game.lower()]
    if not items:
        return f"No scores yet for {game}."
    reverse = game == "Tango"
    items.sort(key=lambda x: x["score"], reverse=reverse)
    return "\n".join(f"**{i['user_id']}** – {i['score']} {i['metric']} ({i['game_date'].split('_')[1]})" for i in items)

# Plot graph
def plot_user(game: str, user: str):
    items = [i for i in fetch_all() if i["raw_game"].lower() == game.lower() and i["user_id"] == user]
    if len(items) < 2:
        return None
    items.sort(key=lambda x: x["timestamp"])
    dates = [i["game_date"].split("_")[1] for i in items]
    scores = [i["score"] for i in items]
    fig, ax = plt.subplots(figsize=(6,3))
    ax.plot(dates, scores, marker="o")
    ax.set_title(f"{user} – {game} over time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Score")
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

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

# Leaderboards
st.header("🏆 Leaderboards")
for game in GAMES:
    with st.expander(f"{game} Leaderboard", expanded=False):
        st.markdown(leaderboard(game), unsafe_allow_html=True)

# Progress graph
st.header("📈 My Progress")
game_choice = st.selectbox("Select Game for Graph", GAMES, key="graph_select")
if st.button("Show Graph", key="show_graph"):
    img_b64 = plot_user(game_choice, user_id)
    if img_b64:
        st.image(f"data:image/png;base64,{img_b64}", caption=f"{user_id}'s {game_choice} Progress")
    else:
        st.info(f"Need at least 2 {game_choice} scores for {user_id} to plot a graph.")