from trackerbazaar.user_manager import UserManager
from trackerbazaar.portfolio import PortfolioUI
from trackerbazaar.dashboard import DashboardUI
from trackerbazaar.cash import CashUI
from trackerbazaar.transactions import TransactionsUI
from trackerbazaar.dividends import DividendsUI

# ...
user_email = st.session_state.get("logged_in_user")
# ...
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
