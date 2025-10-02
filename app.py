import streamlit as st
from pages import submit_score, all_scores, progress, debug

st.set_page_config(page_title="LinkedInowe Wariaty", page_icon="🎮")
st.title("🎮 LinkedInowe Wariaty")

# Initialize session state
if "progress_game" not in st.session_state: st.session_state.progress_game = "Pinpoint"
if "progress_players" not in st.session_state: st.session_state.progress_players = None
if "debug_mode" not in st.session_state: st.session_state.debug_mode = False

tab1, tab2, tab3, tab4 = st.tabs(["📝 Submit Score", "📋 All Scores", "📈 Progress", "⚙️ Debug"])

with tab1: submit_score.show()
with tab2: all_scores.show()
with tab3: progress.show()
with tab4: debug.show()