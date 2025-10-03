import pytest
import streamlit as st
from utils import aws

@pytest.mark.aws  # mark for selective running
def test_read_all_items_real_db():
    AWS_CFG = st.secrets.get("aws", {})

    for table_name in ["game_scores", "raw_game_posts"]:
        table = aws.get_ddb_table(AWS_CFG, table_name)
        assert table is not None, f"Could not connect to table '{table_name}'"

        items = table.scan().get("Items", [])
        print(f"Found {len(items)} items in table '{table_name}'")

        # Verify result is a list
        assert isinstance(items, list)
