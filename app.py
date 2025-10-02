import streamlit as st
import boto3
import re
from datetime import datetime, timedelta
import pandas as pd
import random
import json

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
                def delete_item(self, Key): 
                    self.data = [i for i in self.data if not (i.get('user_id') == Key['user_id'] and i.get('game_date') == Key['game_date'])]
            return MockTable()
    except Exception as e:
        st.error(f"DynamoDB error: {str(e)}.")
        st.stop()

table = get_ddb_table()

# Players, Games, Colors
PLAYERS = ["Mikuś", "Maciuś", "Patryk"]
GAMES = ["Pinpoint", "Queens", "Crossclimb", "Tango"]
COLORS = {"Mikuś": "#00ff88", "Maciuś": "#0077ff", "Patryk": "#cc00ff"}

# Parse LinkedIn post
def parse_post(text: str):
    text = text.strip()
    m = re.search(r"Pinpoint #\d+ \|\s*(\d+)\s*guesses", text, re.IGNORECASE)
    if m: return {"game": "Pinpoint", "score": int(m.group(1)), "metric": "guesses (lower better)"}
    m = re.search(r"Queens #\d+ \|\s*([\d:]+)", text, re.IGNORECASE)
    if m:
        mins, secs = map(int, m.group(1).split(":"))
        return {"game": "Queens", "score": mins*60 + secs, "metric": "seconds (lower better)"}
    m = re.search(r"Crossclimb #\d+ \|\s*(\d+)\s*clues", text, re.IGNORECASE)
    if m: return {"game": "Crossclimb", "score": int(m.group(1)), "metric": "clues (lower better)"}
    m = re.search(r"Tango #\d+ \|\s*(\d+)\s*points", text, re.IGNORECASE)
    if m: return {"game": "Tango", "score": int(m.group(1)), "metric": "points (higher better)"}
    raise ValueError("Could not detect a supported game pattern.")

# Save score
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

# Generate test data
def generate_test_data(user: str, game: str = "Pinpoint"):
    today = datetime.utcnow().date()
    for i in range(4):
        date = today - timedelta(days=i)
        score = random.randint(3, 6)
        item = {
            "user_id": user,
            "game_date": f"{game}_{date.isoformat()}",
            "score": score,
            "metric": "guesses (lower better)",
            "timestamp": (datetime.utcnow() - timedelta(days=i)).replace(hour=12, minute=0, second=0).isoformat(),
            "raw_game": game,
        }
        table.put_item(Item=item)
    return True

# Fetch all scores
def fetch_all():
    try:
        return table.scan().get("Items", [])
    except Exception as e:
        st.error(f"Failed to fetch scores: {str(e)}.")
        return []

# Chart.js plot
def plot_chartjs(df: pd.DataFrame, game: str, players: list):
    if df.empty:
        st.info(f"No data for {game} for selected players.")
        return

    datasets = []
    for player in players:
        player_df = df[df["user_id"] == player].sort_values("Date")
        datasets.append({
            "label": player,
            "data": [{"x": str(d.date()), "y": int(s)} for d, s in zip(player_df["Date"], player_df["Score"])],
            "borderColor": COLORS.get(player, "#ffffff"),
            "backgroundColor": COLORS.get(player, "#ffffff"),
            "fill": False,
            "tension": 0.4,
            "pointRadius": 5,
            "pointHoverRadius": 7
        })

    config = {
        "type": "line",
        "data": {"datasets": datasets},
        "options": {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {"legend": {"display": True, "position": "top"}},
            "scales": {
                "x": {"type": "time", "time": {"unit": "day"}, "title": {"display": True, "text": "Date"}},
                "y": {"title": {"display": True, "text": "Score"}}
            },
            "animation": {"duration": 2000, "easing": "easeOutQuart"},
            "elements": {"line": {"borderWidth": 4}},
            "hover": {"mode": "nearest", "intersect": True}
        }
    }

    html_code = f"""
    <canvas id="myChart" style="width:100%;height:400px;"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        const ctx = document.getElementById('myChart').getContext('2d');
        const config = {json.dumps(config)};
        new Chart(ctx, config);
    </script>
    """
    st.components.v1.html(html_code, height=450)

# --- Streamlit UI ---
st.set_page_config(page_title="LinkedInowe Wariaty", page_icon="🎮")
st.title("🎮 LinkedInowe Wariaty – Game Score Tracker")
st.markdown("Track scores for Mikuś, Maciuś, and Patryk across Pinpoint, Queens, Crossclimb, and Tango!")

# Session state
if "progress_game" not in st.session_state: st.session_state.progress_game = "Pinpoint"
if "progress_players" not in st.session_state: st.session_state.progress_players = PLAYERS
if "debug_mode" not in st.session_state: st.session_state.debug_mode = False

tab1, tab2, tab3, tab4 = st.tabs(["📝 Submit Score", "📋 All Scores", "📈 Progress", "⚙️ Debug"])

# --- Submit Score ---
with tab1:
    st.header("Submit a New Score")
    user_id = st.selectbox("Select Player", PLAYERS, key="submit_player")
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

# --- All Scores ---
with tab2:
    st.header("All Scores")
    items = fetch_all()
    df_all = pd.DataFrame(items)
    if not df_all.empty:
        df_all = df_all.copy()
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

# --- Progress Tab ---
with tab3:
    st.header("Game Progress")
    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        progress_game = st.selectbox("Select Game", GAMES, index=GAMES.index("Pinpoint"), key="progress_game")
    with col2:
        progress_players = st.multiselect("Select Players", PLAYERS, default=st.session_state.progress_players, key="progress_players")
    with col3:
        date_filter = st.selectbox("Date Range", ["Last 7 days","Last 30 days","All"], index=0)

    all_items = fetch_all()
    df_prog = pd.DataFrame(all_items)
    if not df_prog.empty:
        df_prog["Date"] = pd.to_datetime(df_prog["game_date"].apply(lambda x: x.split("_")[1]))
        df_prog = df_prog[df_prog["raw_game"]==progress_game]
        if date_filter=="Last 7 days":
            df_prog = df_prog[df_prog["Date"] >= pd.Timestamp(datetime.utcnow().date()) - pd.Timedelta(days=7)]
        elif date_filter=="Last 30 days":
            df_prog = df_prog[df_prog["Date"] >= pd.Timestamp(datetime.utcnow().date()) - pd.Timedelta(days=30)]
        df_prog = df_prog[df_prog["user_id"].isin(progress_players)]
    else:
        df_prog = pd.DataFrame(columns=["user_id","Date","Score"])

    if not progress_players:
        st.info("Select at least one player")
    else:
        plot_chartjs(df_prog, progress_game, progress_players)

# --- Debug Tab ---
with tab4:
    st.header("Debug / Test Data")
    test_player = st.selectbox("Select Player for Test Data", PLAYERS, key="test_player")
    if st.button("Add Test Data"):
        generate_test_data(test_player)
        st.success(f"Added test data for {test_player}!")
    st.checkbox("Debug Mode", value=st.session_state.debug_mode, key="debug_mode")
