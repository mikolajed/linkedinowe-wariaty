import boto3
import streamlit as st

def get_ddb_table(AWS_CFG, table_name="game_scores"):
    """
    Returns a DynamoDB Table object or a mock in-memory table if credentials are missing.
    table_name: either "game_scores" or "raw_game_posts"
    """
    if AWS_CFG.get("access_key_id"):
        session = boto3.Session(
            region_name=AWS_CFG.get("region", "us-east-1"),
            aws_access_key_id=AWS_CFG.get("access_key_id"),
            aws_secret_access_key=AWS_CFG.get("secret_access_key"),
        )
        ddb = session.resource("dynamodb")
        return ddb.Table(table_name)
    else:
        st.warning(f"No AWS credentials – using in-memory storage for {table_name} (data lost on restart).")
        class MockTable:
            def __init__(self): self.data = []
            def put_item(self, Item): self.data.append(Item)
            def scan(self): return {"Items": self.data}
            def delete_item(self, Key):
                self.data = [
                    i for i in self.data 
                    if not (i.get('user_id') == Key['user_id'] and i.get('timestamp') == Key['timestamp'])
                ]
        return MockTable()
