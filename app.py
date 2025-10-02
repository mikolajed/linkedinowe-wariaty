import streamlit as st
import boto3
import re
from datetime import datetime, timedelta
import pandas as pd
import random

# --- Config / Secrets ---
try:
    AWS_CFG = st.secrets.get("aws", {})
except Exception as e:
    st.error("Missing secrets – add [aws] section in Streamlit Cloud Secrets tab.")
    st.stop()

# --- AWS DynamoDB (or mock) ---
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

# --- Players, Games, Colors ---
PLAYERS = ["Mikuś", "Maciuś", "Patryk"]
GAMES = ["Pinpoint", "Queens", "Crossclimb", "Tango"]
COLORS = {"Mikuś": "#00ff88", "Maciuś": "#0077ff", "Patryk": "#cc00ff"}

# --- Parse LinkedIn post ---
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

# --- Save score ---
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

# --- Generate test data ---
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

# --- Fetch all scores ---
def fetch_all():
    try:
        return table.scan().get("Items", [])
    except Exception as e:
        st.error(f"Failed to fetch scores: {str(e)}.")
        return []

# --- Streamlit UI ---
st.set_page_config(page_title="LinkedInowe Wariaty", page_icon="🎮")
st.title("🎮 LinkedInowe Wariaty – Game Score Tracker")
st.markdown("Track scores for Mikuś, Maciuś, and Patryk across Pinpoint, Queens, Crossclimb, and Tango!")

# --- Session state ---
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

# --- Progress Tab (Plotly-based) ---
with tab3:
    st.header("Game Progress")
    
    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        progress_game = st.selectbox("Select Game", GAMES, index=GAMES.index("Pinpoint"))
    with col2:
        progress_players = st.multiselect("Select Players", PLAYERS, default=PLAYERS)
    with col3:
        date_filter = st.selectbox("Date Range", ["Last 7 days","Last 30 days","All"], index=0)

    # Fetch and filter data
    all_items = fetch_all()
    df_prog = pd.DataFrame(all_items)
    
    if df_prog.empty:
        st.info("No scores yet.")
    else:
        df_prog["Date"] = pd.to_datetime(df_prog["game_date"].apply(lambda x: x.split("_")[1]))
        df_prog = df_prog[df_prog["raw_game"]==progress_game]
        
        if date_filter=="Last 7 days":
            df_prog = df_prog[df_prog["Date"] >= datetime.utcnow() - timedelta(days=7)]
        elif date_filter=="Last 30 days":
            df_prog = df_prog[df_prog["Date"] >= datetime.utcnow() - timedelta(days=30)]

        df_prog = df_prog[df_prog["user_id"].isin(progress_players)]

        if df_prog.empty:
            st.info(f"No scores for {progress_game} in selected players/date range.")
        else:
            import plotly.express as px
            fig = px.line(
                df_prog,
                x="Date",
                y="score",
                color="user_id",
                markers=True,
                line_shape="spline",
                labels={"score":"Score", "user_id":"Player"}
            )
            
            # Custom colors
            for trace in fig.data:
                player_name = trace.name
                trace.line.color = COLORS.get(player_name, "#ffffff")
                trace.marker.color = COLORS.get(player_name, "#ffffff")
                trace.line.width = 4
                trace.marker.size = 8

            fig.update_layout(
                title=f"{progress_game} Progress",
                xaxis_title="Date",
                yaxis_title="Score",
                template="plotly_dark",
                font=dict(family="Arial", size=12),
                plot_bgcolor="#1f1f1f",
                paper_bgcolor="#1f1f1f",
                legend=dict(font=dict(size=12)),
                margin=dict(l=20, r=20, t=50, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)

# --- Debug Tab ---
with tab4:
    st.header("Debug / Test Data")
    test_player = st.selectbox("Select Player for Test Data", PLAYERS, key="test_player")
    if st.button("Add Test Data"):
        generate_test_data(test_player)
        st.success(f"Added test data for {test_player}!")
    st.checkbox("Debug Mode", value=st.session_state.debug_mode, key="debug_mode")
