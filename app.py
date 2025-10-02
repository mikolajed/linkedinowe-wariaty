# app.py
import streamlit as st
import boto3
import re
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os

# 1. Config/Secrets
try:
    AUTH_CFG = st.secrets["auth"]
    AWS_CFG = st.secrets.get("aws", {})
except Exception as e:
    st.error("Missing secrets – copy .streamlit/secrets.toml.example to .streamlit/secrets.toml and fill it.")
    st.stop()

# 2. AWS DynamoDB (or mock for testing)
def get_ddb_table():
    if os.getenv("AWS_ACCESS_KEY_ID") or AWS_CFG.get("access_key_id"):
        session = boto3.Session(
            region_name=AWS_CFG.get("region", "us-east-1"),
            aws_access_key_id=AWS_CFG.get("access_key_id"),
            aws_secret_access_key=AWS_CFG.get("secret_access_key"),
        )
        ddb = session.resource("dynamodb")
        return ddb.Table("GameScores")
    else:
        st.warning("No AWS credentials – using in-memory storage (data lost on restart).")
        class MockTable:
            def __init__(self): self.data = []
            def put_item(self, Item): self.data.append(Item)
            def scan(self): return {"Items": self.data}
        return MockTable()

table = get_ddb_table()

# 3. User Mapping (LinkedIn sub -> friendly name)
USER_MAP = {
    # Add real LinkedIn sub values here after first login
    # Example: "urn:li:person:AbCdEfGhIj": "Me",
}

# 4. Auth – LinkedIn OIDC
if not st.session_state.get("authenticated"):
    st.info("Sign in with LinkedIn to continue")
    if st.button("Sign in with LinkedIn"):
        st.login(
            provider="generic",
            client_id=AUTH_CFG["client_id"],
            client_secret=AUTH_CFG["client_secret"],
            server_metadata_url=AUTH_CFG["server_metadata_url"],
            redirect_uri=AUTH_CFG["redirect_uri"],
            cookie_secret=AUTH_CFG["cookie_secret"]
        )
    st.stop()

user_claims = st.user
linkedin_sub = user_claims.get("sub")
user_id = USER_MAP.get(linkedin_sub)

if not user_id:
    st.error(f"Unknown LinkedIn account ({linkedin_sub}). Add it to USER_MAP in app.py.")
    if st.button("Logout"):
        st.logout()
    st.stop()

st.success(f"Welcome, {user_id}! ({user_claims.get('name', '')})")
if st.button("Logout"):
    st.logout()

# 5. Parsing Logic
def parse_post(text: str):
    m = re.search(r"Pinpoint #\d+ \|\s*(\d+)\s*guesses", text)
    if m:
        return {"game": "Pinpoint", "score": int(m.group(1)), "metric": "guesses (lower better)"}
    m = re.search(r"Queens #\d+ \|\s*([\d:]+)", text)
    if m:
        time_str = m.group(1)
        mins, secs = map(int, time_str.split(":"))
        return {"game": "Queens", "score": mins*60 + secs, "metric": "seconds (lower better)"}
    m = re.search(r"Crossclimb #\d+ \|\s*(\d+)\s*clues", text)
    if m:
        return {"game": "Crossclimb", "score": int(m.group(1)), "metric": "clues (lower better)"}
    raise ValueError("Could not detect a supported game pattern.")

# 6. Save to DynamoDB
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

# 7. Read/Display
def fetch_all():
    return table.scan().get("Items", [])

def leaderboard(game: str):
    items = [i for i in fetch_all() if i["raw_game"] == game]
    if not items:
        return "No scores yet for this game."
    items.sort(key=lambda x: x["score"])
    return "\n".join(f"**{i['user_id']}** – {i['score']} {i['metric']} ({i['game_date'].split('_')[1]})" for i in items)

def plot_user(game: str, user: str):
    items = [i for i in fetch_all() if i["raw_game"] == game and i["user_id"] == user]
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

# 8. UI
st.header("Submit a new result")
post = st.text_area("Paste the LinkedIn share text here", height=150)
if st.button("Save score"):
    if not post.strip():
        st.error("Paste something first!")
    else:
        try:
            parsed = parse_post(post)
            save_score(user_id, parsed)
            st.success(f"Saved **{parsed['game']}** – score {parsed['score']}")
        except ValueError as e:
            st.error(str(e))

st.subheader("Leaderboard")
game_choice = st.selectbox("Game", ["Pinpoint", "Queens", "Crossclimb"])
st.markdown(leaderboard(game_choice), unsafe_allow_html=True)

st.subheader("My progress graph")
if st.button("Show graph"):
    img_b64 = plot_user(game_choice, user_id)
    if img_b64:
        st.image(f"data:image/png;base64,{img_b64}")
    else:
        st.info("Need at least 2 entries to plot a graph.")