from trackerbazaar.user_manager import UserManager
from trackerbazaar.portfolio import PortfolioUI
from trackerbazaar.dashboard import DashboardUI
from trackerbazaar.cash import CashUI
from trackerbazaar.transactions import TransactionsUI
from trackerbazaar.dividends import DividendsUI

def main():
    st.sidebar.title("📌 Navigation")
    choice = st.sidebar.radio("Go to", ["Portfolios", "Dashboard", "Cash", "Transactions", "Dividends", "Logout"])

    user_manager = UserManager()
    user_email = st.session_state.get("logged_in_user")

    if not user_manager.is_logged_in() and choice != "Logout":
        user_manager.login_form()
        return

    if choice == "Portfolios":
        PortfolioUI(user_email).show()
    elif choice == "Dashboard":
        DashboardUI(user_email).show()
    elif choice == "Cash":
        CashUI(user_email).show()
    elif choice == "Transactions":
        TransactionsUI(user_email).show()
    elif choice == "Dividends":
        DividendsUI(user_email).show()
    elif choice == "Logout":
        user_manager.logout()
        st.success("✅ Logged out successfully")
        st.rerun()
