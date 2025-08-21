# trackerbazaar/signup.py
import streamlit as st
from trackerbazaar.users import UserManager

def render_signup():
    user_manager = UserManager()
    user_manager.signup()
