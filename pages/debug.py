import streamlit as st
from utils import aws, data
from constants import PLAYERS

def show():
    AWS_CFG = st.secrets.get("aws", {})
    table = aws.get_ddb_table(AWS_CFG)

    st.header("Debug / Test Data")
    test_player = st.selectbox("Select Player for Test Data", PLAYERS, key="test_player")
    if st.button("Add Test Data"):
        data.generate_test_data(table, test_player)
        st.success(f"Added test data for {test_player}!")
    st.checkbox("Debug Mode", value=st.session_state.debug_mode, key="debug_mode")
