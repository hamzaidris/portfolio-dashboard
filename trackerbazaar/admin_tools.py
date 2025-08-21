# trackerbazaar/admin_tools.py
import streamlit as st
import os
import sqlite3
from trackerbazaar.data import DB_FILE, init_db

def show_admin_tools():
    st.header("🛠️ Admin Tools")

    st.write(f"**Current DB file:** `{DB_FILE}`")

    # Check if DB exists
    if os.path.exists(DB_FILE):
        st.success("✅ Database file exists")
    else:
        st.warning("⚠️ Database file does not exist")

    # Button: Initialize / Reset DB
    if st.button("🔄 Rebuild Database (Drop & Recreate All Tables)"):
        try:
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)  # delete old DB file
            init_db()  # re-create fresh DB with tables
            st.success("✅ Database has been rebuilt successfully!")
        except Exception as e:
            st.error(f"❌ Failed to rebuild DB: {e}")

    # Button: Inspect tables
    if st.button("📋 Show Tables"):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            if tables:
                st.write("### Tables in DB:")
                for t in tables:
                    st.write(f"- {t[0]}")
            else:
                st.info("No tables found in database.")
        except Exception as e:
            st.error(f"❌ Failed to read tables: {e}")
