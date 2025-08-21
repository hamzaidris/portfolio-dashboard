import streamlit as st
from trackerbazaar.tracker import PortfolioTracker
from trackerbazaar.auth import create_user, login_user

# ---------------------------
# Initialize session state
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "login"  # default page

# ---------------------------
# Render Register Page
# ---------------------------
def render_register():
    st.header("Register")
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")
        if submit:
            if not username or not email or not password:
                st.error("All fields are required.")
            elif create_user(username, email, password):
                st.success("Account created! Please login.")
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Username or email already exists. Try again.")

# ---------------------------
# Render Login Page
# ---------------------------
def render_login():
    st.header("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            user_data = login_user(username, password)
            if user_data:
                st.session_state.authenticated = True
                st.session_state.user_data = user_data
                st.session_state.username = username  # Store username directly
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.write("Don't have an account?")
    if st.button("Register here"):
        st.session_state.page = "register"
        st.rerun()

# ---------------------------
# Render Dashboard
# ---------------------------
def render_dashboard():
    st.header("Portfolio Dashboard")

    # Use the username stored directly in the session state
    if st.session_state.username:
        tracker = PortfolioTracker(st.session_state.username)
    else:
        st.error("No user data found. Please log in again.")
        st.session_state.authenticated = False
        st.session_state.page = "login"
        st.rerun()
        return

    st.success(f"Welcome, {st.session_state.username}!")

    # Example features (add your own pages here)
    st.write("Here will be portfolio stats, transactions, dividends, etc.")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_data = None
        st.session_state.username = None
        st.session_state.page = "login"
        st.rerun()

# ---------------------------
# Main App
# ---------------------------
def main():
    if st.session_state.page == "register":
        render_register()
    elif st.session_state.page == "login":
        render_login()
    elif st.session_state.page == "dashboard":
        if st.session_state.authenticated:
            render_dashboard()
        else:
            st.session_state.page = "login"
            st.rerun()

if __name__ == "__main__":
    main()
