# trackerbazaar/users.py
import streamlit as st
from datetime import datetime

class UserManager:
    def __init__(self):
        self.users = {"user1@example.com": "password123", "user2@example.com": "password456"}  # Sample user database
        if "logged_in_user" not in st.session_state:
            st.session_state.logged_in_user = None
        if "portfolios" not in st.session_state:
            st.session_state.portfolios = {}

    def login(self):
        st.sidebar.header("User Login")
        email = st.sidebar.text_input("Email")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if email in self.users and self.users[email] == password:
                st.session_state.logged_in_user = email
                st.success(f"Logged in as {email}")
                st.rerun()
            else:
                st.sidebar.error("Invalid email or password")
        if st.sidebar.button("Logout") and st.session_state.logged_in_user:
            st.session_state.logged_in_user = None
            st.session_state.portfolios = {}
            st.success("Logged out successfully")
            st.rerun()

    def signup(self):
        st.header("Sign Up")
        st.write("Create a new account to manage your portfolios.")
        new_email = st.text_input("New Email", key="signup_email")
        new_password = st.text_input("New Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        
        if st.button("Sign Up", key="signup_submit"):
            if new_email in self.users:
                st.error("Email already registered. Please use a different email or log in.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif not new_email or not new_password:
                st.error("Email and password cannot be empty.")
            else:
                self.users[new_email] = new_password
                st.success(f"Account created for {new_email}. You can now log in.")
                st.session_state.logged_in_user = new_email
                st.rerun()

    def is_logged_in(self):
        return st.session_state.logged_in_user is not None

    def get_current_user(self):
        return st.session_state.logged_in_user
