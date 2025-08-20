import streamlit as st
import pandas as pd
from .tracker import PortfolioTracker

def render_transactions(tracker):
    st.header("Transaction History")
    if tracker.transactions:
        trans_df = pd.DataFrame(tracker.transactions)
        if not trans_df.empty:
            trans_df['date'] = pd.to_datetime(trans_df['date']).dt.strftime('%Y-%m-%d')
            trans_df['Select'] = False
            edited_df = st.data_editor(
                trans_df,
                column_config={
                    "Select": st.column_config.CheckboxColumn(),
                    "total": st.column_config.NumberColumn(format="PKR %.2f"),
                    "realized": st.column_config.NumberColumn(format="PKR %.2f"),
                    "price": st.column_config.NumberColumn(format="PKR %.2f"),
                    "fee": st.column_config.NumberColumn(format="PKR %.2f")
                },
                use_container_width=True,
                hide_index=False
            )
            selected = edited_df[edited_df['Select']].index.tolist()
            if st.button("Delete Selected Transactions"):
                try:
                    for index in sorted(selected, reverse=True):
                        tracker.delete_transaction(index)
                    st.success("Selected transactions deleted successfully!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")
    else:
        st.info("No transactions recorded. Add transactions via 'Add Transaction'.")
