import streamlit as st
from trackerbazaar.tracker import PortfolioTracker
from trackerbazaar.auth import login_user, create_user

def main():
    st.set_page_config(page_title="Portfolio Dashboard", layout="wide")

    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_data = None
        st.session_state.data_changed = False

    if not st.session_state.logged_in:
        st.sidebar.header("User Authentication")
        auth_choice = st.sidebar.radio("Choose Action", ["Login", "Register"])

        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if auth_choice == "Login":
            if st.sidebar.button("Login"):
                user_data = login_user(username, password)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user_data = user_data
                    st.success(f"Welcome back, {user_data['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        else:  # Register
            email = st.sidebar.text_input("Email")
            if st.sidebar.button("Register"):
                if create_user(username, email, password):
                    st.success("User registered successfully! Please log in.")
                else:
                    st.error("Username or email already exists. Try again.")

    else:
        st.sidebar.success(f"Logged in as {st.session_state.user_data['username']}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.rerun()

        # Load tracker for the logged-in user
        tracker = PortfolioTracker(st.session_state.user_data["username"])

        st.title("📊 Portfolio Dashboard")

        # Example navigation (you can expand)
        menu = st.sidebar.radio("Navigate", ["Portfolio", "Add Dividend"])

        if menu == "Portfolio":
            st.subheader("Portfolio Overview")
            tracker.render_portfolio()  # assuming you have this function
        elif menu == "Add Dividend":
            from trackerbazaar.dividends import render_add_dividend
            render_add_dividend(tracker)

if __name__ == "__main__":
    main()
