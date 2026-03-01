import streamlit as st
import psycopg2
import pandas as pd
import time

st.set_page_config(page_title="GuardianAI Dashboard", layout="wide")

st.title("🛡️ GuardianAI: Contextual Moderation Feed")
st.write("Monitoring Reasoning Agent...")

def get_data():
    try:
        conn = psycopg2.connect(
            dbname="moderation_db", user="admin", password="password123", host="127.0.0.1", port="5432"
        )
        # We fetch the ID, Status, and Content. 
        query = "SELECT id, status, content_text FROM content_items ORDER BY id DESC LIMIT 10"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"DB Connection Error: {e}")
        return pd.DataFrame()

placeholder = st.empty()

while True:
    with placeholder.container():
        df = get_data()
        if not df.empty:
            # Display stats at the top
            rejections = len(df[df['status'] == 'REJECTED'])
            st.metric("Recent Rejections", rejections)

            # Styled Table
            def color_status(val):
                color = '#ff4b4b' if val == 'REJECTED' else '#00f900' if val == 'APPROVED' else '#f9f900'
                return f'background-color: {color}; color: black; font-weight: bold'

            st.table(df.style.applymap(color_status, subset=['status']))
        
        time.sleep(3) # Auto-refresh every 3 seconds
