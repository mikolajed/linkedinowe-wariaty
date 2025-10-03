import streamlit as st
from pages import submit, scores, progress, posts, developer
from constants import GAMES

st.set_page_config(page_title="LinkedInowe Wariaty", page_icon="🎮")
st.title("🎮 LinkedInowe Wariaty")

# Session state
if "chosen_game" not in st.session_state:
    st.session_state.chosen_game = GAMES[0]
if "chosen_player" not in st.session_state:
    st.session_state.chosen_player = None
if "allow_pysiek" not in st.session_state:
    st.session_state.allow_pysiek = True

# Tabs
tab_submit, tab_scores, tab_posts, tab_progress, tab_developer = st.tabs([
    "📝 Submit", "📋 Scores", "🗒️ Posts", "📈 Progress", "🛠️ Developer"
])

with tab_submit: submit.show()
with tab_scores: scores.show()
with tab_posts: posts.show()
with tab_progress: progress.show()
with tab_developer: developer.show()
