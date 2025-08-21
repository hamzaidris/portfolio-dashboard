import streamlit as st

# Import from our package
try:
    from trackerbazaar import (
        PortfolioManager,
        PortfolioTracker,
        init_db
    )
except Exception as e:
    st.error(f"⚠️ Failed to import core modules: {e}")
    st.stop()

# ✅ Always initialize DB on startup
try:
    init_db()
except Exception as e:
    st.error(f"⚠️ Database initialization failed: {e}")
    st.stop()


# --------------------------
# Streamlit App UI
# --------------------------

st.set_page_config(page_title="TrackerBazaar", layout="wide")

st.title("📊 TrackerBazaar")

tab1, tab2, tab3 = st.tabs(["Trade Manager", "Dashboard", "FIRE Tracker"])

# Trade Manager
with tab1:
    st.subheader("💼 Manage Your Trades")
    try:
        pm = PortfolioManager()
        portfolios = pm.list_portfolios()
        if not portfolios:
            st.info("No portfolios yet. Please create one.")
        else:
            for p in portfolios:
                st.write(f"- {p[1]} (Owner: {p[2]})")
    except Exception as e:
        st.error(f"⚠️ Error loading portfolios: {e}")

# Dashboard
with tab2:
    st.subheader("📈 Portfolio Dashboard")
    try:
        pt = PortfolioTracker()
        summary = pt.get_summary()
        if not summary:
            st.info("No data available yet.")
        else:
            st.write(summary)
    except Exception as e:
        st.error(f"⚠️ Error loading dashboard: {e}")

# FIRE Tracker
with tab3:
    st.subheader("🔥 Financial Independence Tracker")
    st.info("FIRE goals and progress will appear here soon.")
