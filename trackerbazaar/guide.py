import streamlit as st

def render_guide():
    st.header("📘 Guide")
    st.markdown("""
    **Welcome to TrackerBazaar (fixed baseline).**  
    1) Go to **Cash** → deposit some cash.  
    2) Go to **Add Transaction** → add a BUY for any PSX symbol found in **Current Prices**.  
    3) Check **Dashboard** and **Portfolio**.
    """)
