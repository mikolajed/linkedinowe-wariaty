import boto3
import streamlit as st

def get_ddb_table(AWS_CFG, table_name="game-scores"):
    """
    Returns a DynamoDB Table object or a mock in-memory table if credentials are missing.
    
    Parameters:
    - AWS_CFG: dict with AWS credentials from st.secrets
    - table_name: str, either "game-scores" or "raw_game_posts"
    """
    if AWS_CFG.get("access_key_id") and AWS_CFG.get("secret_access_key"):
        session_kwargs = {
            "aws_access_key_id": AWS_CFG.get("access_key_id"),
            "aws_secret_access_key": AWS_CFG.get("secret_access_key"),
        }
        if AWS_CFG.get("region"):
            session_kwargs["region_name"] = AWS_CFG["region"]

        try:
            session = boto3.Session(**session_kwargs)
            ddb = session.resource("dynamodb")
            table = ddb.Table(table_name)
            # Check table existence
            table.meta.client.describe_table(TableName=table_name)
            return table
        except Exception as e:
            st.error(f"Failed to access table '{table_name}': {str(e)}. Check table name and permissions.")
            return None
    else:
        st.warning(f"No AWS credentials – using in-memory storage for {table_name} (data lost on restart).")
        
        class MockTable:
            def __init__(self):
                self.data = []

            def put_item(self, Item):
                self.data.append(Item)

            def scan(self):
                return {"Items": self.data}

            def delete_item(self, Key):
                self.data = [
                    i for i in self.data
                    if not (i.get('user_id') == Key['user_id'] and i.get('timestamp') == Key['timestamp'])
                ]

        return MockTable()