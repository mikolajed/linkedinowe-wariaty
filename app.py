import streamlit as st
from pages import submit_score, all_scores, progress, all_posts, debug
from constants import GAMES

st.set_page_config(page_title="LinkedInowe Wariaty", page_icon="🎮")
st.title("🎮 LinkedInowe Wariaty")

if "progress_game" not in st.session_state:
    st.session_state.progress_game = GAMES[0]
if "progress_players" not in st.session_state:
    st.session_state.progress_players = None
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Submit Score", "📋 All Scores", "🗒️ All Posts", "📈 Progress", "⚙️ Debug"
])

with tab1: submit_score.show()
#with tab2: all_scores.show()
#with tab3: all_posts.show()
#with tab4: progress.show()
with tab5: debug.show()
