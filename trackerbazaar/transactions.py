import streamlit as st
import pandas as pd

def render_transactions(tracker):
    st.header("🧾 Transactions")
    if tracker.transactions:
        st.dataframe(pd.DataFrame(tracker.transactions))
    else:
        st.info("No transactions yet.")
