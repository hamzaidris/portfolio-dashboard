import streamlit as st

def render_broker_fees(tracker):
    st.header("💸 Broker Fees")
    pct = st.number_input(
        "Broker Fee %",
        min_value=0.0, max_value=5.0,
        value=float(tracker.broker_fee_pct or 0.0),
        step=0.05
    )
    if st.button("Save Fee"):
        tracker.set_broker_fee_pct(pct)
        st.success("Saved.")
