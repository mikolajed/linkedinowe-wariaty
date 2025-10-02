import streamlit as st
import boto3
import re
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import random
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

# Generate test data for past 4 days
def generate_test_data(user: str, game: str = "Pinpoint"):
    today = datetime.utcnow().date()
    for i in range(4):
        date = today - timedelta(days=i)
        score = random.randint(3, 6)  # Random Pinpoint guesses
        item = {
            "user_id": user,
            "game_date": f"{game}_{date.isoformat()}",
            "score": score,
            "metric": "guesses (lower better)",
            "timestamp": (datetime.utcnow() - timedelta(days=i)).replace(hour=12, minute=0, second=0, microsecond=0).isoformat(),
            "raw_game": game,
        }
        try:
            table.put_item(Item=item)
        except Exception as e:
            st.error(f"Failed to add test data for {date}: {str(e)}")
            return False
    return True

# Fetch all
def fetch_all():
    try:
        return table.scan().get("Items", [])
    except Exception as e:
        st.error(f"Failed to fetch scores: {str(e)}. Check DynamoDB permissions.")
        return []

# Plot progress
def plot_user(game: str, user: str):
    items = [i for i in fetch_all() if i["raw_game"].lower() == game.lower() and i["user_id"] == user]
    if not items:
        return None, []
    items.sort(key=lambda x: x["timestamp"])
    dates = [i["game_date"].split("_")[1] for i in items]
    scores = [int(i["score"]) for i in items]  # Convert Decimal to int
    df = pd.DataFrame({"Date": dates, "Score": scores, "Timestamp": [i["timestamp"] for i in items]})
    
    # Debug: Log data
    st.write(f"**Debug**: Plotting {len(dates)} points: {dates}, {scores}")
    
    # Plotly graph
    fig = px.line(
        df,
        x="Date",
        y="Score",
        title=f"{user}'s {game} Progress",
        markers=True,
        template="plotly_dark"
    )
    fig.update_traces(
        line=dict(color="#00ff88", width=4),
        marker=dict(size=8),
        opacity=0,  # Start invisible for animation
        transition=dict(duration=2000, easing="cubic-in-out")
    )
    fig.update_layout(
        font=dict(family="Arial", size=12, color="#ffffff"),
        title_font_size=20,
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(ticks="", tickfont=dict(size=12), showgrid=False),
        yaxis=dict(ticks="", tickfont=dict(size=12), showgrid=False),
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="#1f1f1f",
        paper_bgcolor="#1f1f1f",
        animations=[dict(
            method="animate",
            args=[[{"opacity": 1}], {"frame": {"duration": 2000, "redraw": True}, "fromcurrent": True, "mode": "immediate"}]
        )]
    )
    return fig, df

# UI
st.set_page_config(page_title="LinkedInowe Wariaty", page_icon="🎮")
st.title("🎮 LinkedInowe Wariaty – Game Score Tracker")
st.markdown("Track scores for Mikuś, Maciuś, and Patryk across Pinpoint, Queens, Crossclimb, and more!")

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 Submit Score", "📋 All Scores", "📈 Progress"])

with tab1:
    # Score submission
    st.header("Submit a New Score")
    user_id = st.selectbox("Select Player", PLAYERS, help="Choose who you are.", key="submit_player")
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

    # Test data button
    st.subheader("Generate Test Data")
    test_player = st.selectbox("Select Player for Test Data", PLAYERS, key="test_player")
    if st.button("Add Test Data (Pinpoint, Past 4 Days)"):
        success = generate_test_data(test_player, "Pinpoint")
        if success:
            st.success(f"Added 4 test Pinpoint scores for {test_player}!")
        else:
            st.error("Failed to add test data. Check DynamoDB permissions.")

    # Test buttons
    st.subheader("DynamoDB Test")
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

with tab2:
    # All entries with filtering
    st.header("All Scores")
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

with tab3:
    # Progress tab
    st.header("My Progress")
    col1, col2 = st.columns(2)
    with col1:
        progress_player = st.selectbox("Select Player", PLAYERS, key="progress_player")
    with col2:
        progress_game = st.selectbox("Select Game", GAMES, key="progress_game")
    if st.button("Show Progress", key="show_progress"):
        fig, df = plot_user(progress_game, progress_player)
        if fig:
            st.write(f"**Debug**: Found {len(df)} scores for {progress_player} in {progress_game}")
            st.dataframe(df[["Date", "Score"]], use_container_width=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No scores for {progress_player} in {progress_game}. Use 'Add Test Data' in Submit Score tab to add scores.")