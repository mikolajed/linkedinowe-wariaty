import boto3
import streamlit as st

def get_ddb_table(AWS_CFG):
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
