import streamlit as st

def render_cash(tracker):
    st.header("💵 Cash")
    st.write(f"Current cash: **{tracker.cash:,.2f} PKR**")
    col1, col2 = st.columns(2)
    with col1:
        amt = st.number_input("Deposit amount", min_value=0.0, value=0.0, step=100.0)
        if st.button("Deposit"):
            tracker.deposit_cash(amt)
            st.success(f"Deposited {amt:,.2f}")
    with col2:
        w = st.number_input("Withdraw amount", min_value=0.0, value=0.0, step=100.0)
        if st.button("Withdraw"):
            tracker.withdraw_cash(w)
            st.success(f"Withdrew {w:,.2f}")
