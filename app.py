
import os
import streamlit as st
import pandas as pd

from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from services.google_sheets import get_google_sheets_service
from services.settings_service import get_settings
from services.transaction_service import add_transaction
from datetime import date, datetime
from utils.calculations import calculate_monthly_summary
from services.finance_service import get_financial_data
from datetime import date

from services.transaction_service import (
    get_transactions,
    update_transaction,
    delete_transaction
)
from services.visualization_service import (
    income_expense_chart,
    category_expense_chart,
    daily_expense_chart,
    savings_trend_chart,
    top_spending_categories
)

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

st.set_page_config(
    page_title="Personal Money Manager",
    page_icon="💰",
    layout="wide"
)


# --------------------------------------------------
# GOOGLE SHEETS CONNECTION
# --------------------------------------------------

@st.cache_resource
def connect_google_sheets():
    return get_google_sheets_service()


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title("💰 Personal Money Manager")
st.caption("Manage your income and expenses in one place.")

if not SPREADSHEET_ID:
    st.error("SPREADSHEET_ID is missing from .env")
    st.stop()

try:
    service = connect_google_sheets()

    settings = get_settings(
        service,
        SPREADSHEET_ID
    )

except Exception as error:
    st.error(f"Unable to connect to Google Sheets: {error}")
    st.stop()


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a page",
    [
        "Dashboard",
        "Add Transaction",
        "Transaction History",
        "Monthly Reports",
        "Settings"
    ]
)


# --------------------------------------------------
# ADD TRANSACTION PAGE
# --------------------------------------------------

if page == "Add Transaction":

    st.header("Add Transaction")

    transaction_type = st.radio(
        "Transaction Type",
        ["Expense", "Income"],
        horizontal=True
    )

    st.divider()

    with st.form("transaction_form"):

        transaction_date = st.date_input(
            "Transaction Date"
        )

        if transaction_type == "Expense":

            category = st.selectbox(
                "Expense Category",
                settings["expense_categories"]
            )

        else:

            category = st.selectbox(
                "Income Source",
                settings["income_sources"]
            )

        description = st.text_input(
            "Description",
            placeholder="Example: Lunch, Monthly Salary"
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=10.0,
            format="%.2f"
        )

        payment_method = st.selectbox(
            "Payment Method",
            settings["payment_methods"]
        )

        notes = st.text_area(
            "Notes (Optional)"
        )

        submitted = st.form_submit_button(
            "Save Transaction",
            use_container_width=True
        )

        if submitted:

            if amount <= 0:
                st.error("Please enter an amount greater than zero.")

            elif not description.strip():
                st.error("Please enter a description.")

            elif not category:
                st.error("Please select a category or income source.")

            elif not payment_method:
                st.error("Please select a payment method.")

            else:

                try:

                    response = add_transaction(
                        service=service,
                        spreadsheet_id=SPREADSHEET_ID,
                        transaction_date=transaction_date,
                        transaction_type=transaction_type,
                        category=category,
                        description=description.strip(),
                        amount=amount,
                        payment_method=payment_method,
                        notes=notes.strip()
                    )

                    updated_range = response.get(
                        "updates", {}
                    ).get("updatedRange", "Transactions")

                    st.success(
                        f"{transaction_type} saved successfully!"
                    )

                    st.write(
                        f"Saved to: {updated_range}"
                    )

                    st.balloons()

                except (ValueError, HttpError) as error:

                    st.error(f"Unable to save transaction: {error}")

                except Exception as error:

                    st.error(f"Unexpected error: {error}")


# --------------------------------------------------
# OTHER PAGES - TEMPORARY PLACEHOLDERS
# --------------------------------------------------



elif page == "Dashboard":

    st.header("Financial Dashboard")
    st.caption("Your financial overview and spending insights")

    try:

        # -----------------------------------------
        # 1. FETCH FINANCIAL DATA
        # -----------------------------------------

        finance_data = get_financial_data(
            service,
            SPREADSHEET_ID
        )

        initial_balance = finance_data["initial_balance"]
        starting_date = finance_data["starting_date"]

        df = finance_data["transactions"].copy()

        # -----------------------------------------
        # 2. DATA CLEANING
        # -----------------------------------------

        if not df.empty:

            df["Date"] = pd.to_datetime(
                df["Date"],
                errors="coerce"
            )

            df["Amount"] = pd.to_numeric(
                df["Amount"],
                errors="coerce"
            )

            df["Type"] = (
                df["Type"]
                .astype(str)
                .str.strip()
                .str.title()
            )

            df = df.dropna(
                subset=["Date", "Amount"]
            )

            df = df[
                df["Type"].isin(["Income", "Expense"])
            ].copy()

            df = df[
                df["Date"] >= pd.Timestamp(starting_date)
            ].copy()

            df = df.sort_values(
                ["Date", "Created At"],
                kind="stable"
            )

        # -----------------------------------------
        # 3. MONTH SELECTION
        # -----------------------------------------

        current_month = date.today().strftime("%B %Y")

        month_options = {current_month}

        if not df.empty:

            for transaction_date in df["Date"]:

                month_options.add(
                    transaction_date.strftime("%B %Y")
                )

        month_options = sorted(
            month_options,
            key=lambda x: datetime.strptime(x, "%B %Y")
        )

        selected_month = st.selectbox(
            "Select Month",
            month_options,
            index=month_options.index(current_month)
        )

        selected_month_date = datetime.strptime(
            selected_month,
            "%B %Y"
        ).date()

        # -----------------------------------------
        # 4. FINANCIAL SUMMARY
        # -----------------------------------------

        summary = calculate_monthly_summary(
            df,
            initial_balance,
            starting_date,
            selected_month_date
        )

        st.divider()

        col1, col2 = st.columns(2)

        col1.metric(
            "Opening Balance",
            f"₹{summary['opening_balance']:,.2f}"
        )

        col2.metric(
            "Current Balance",
            f"₹{summary['closing_balance']:,.2f}"
        )

        col3, col4 = st.columns(2)

        col3.metric(
            "Total Income",
            f"₹{summary['total_income']:,.2f}"
        )

        col4.metric(
            "Total Expenses",
            f"₹{summary['total_expenses']:,.2f}"
        )

        # -----------------------------------------
        # 5. FILTER SELECTED MONTH
        # -----------------------------------------

        month_start = pd.Timestamp(
            selected_month_date.year,
            selected_month_date.month,
            1
        )

        month_end = (
            month_start + pd.offsets.MonthEnd(0)
        )

        monthly_df = df[
            (df["Date"] >= month_start) &
            (df["Date"] <= month_end)
        ].copy()

        st.divider()

        # -----------------------------------------
        # 6. MONTHLY INCOME VS EXPENSES
        # -----------------------------------------

        st.subheader("Income vs Expenses")

        st.plotly_chart(
            income_expense_chart(df),
            use_container_width=True
        )

        st.divider()

        # -----------------------------------------
        # 7. CATEGORY AND DAILY EXPENSE CHARTS
        # -----------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Category-wise Spending")

            if not monthly_df.empty and (
                monthly_df["Type"] == "Expense"
            ).any():

                st.plotly_chart(
                    category_expense_chart(monthly_df),
                    use_container_width=True
                )

            else:
                st.info("No expenses recorded this month.")

        with col2:

            st.subheader("Daily Expense Trend")

            if not monthly_df.empty and (
                monthly_df["Type"] == "Expense"
            ).any():

                st.plotly_chart(
                    daily_expense_chart(monthly_df),
                    use_container_width=True
                )

            else:
                st.info("No daily expenses available.")

        st.divider()

        # -----------------------------------------
        # 8. SAVINGS / BALANCE TREND
        # -----------------------------------------

        st.subheader("Balance Trend")

        if not df.empty:

            st.plotly_chart(
                savings_trend_chart(
                    df,
                    initial_balance
                ),
                use_container_width=True
            )

        else:
            st.info("No transactions available for balance trend.")

        st.divider()

        # -----------------------------------------
        # 9. TOP SPENDING CATEGORIES
        # -----------------------------------------

        st.subheader("Top 5 Spending Categories")

        if not monthly_df.empty and (
            monthly_df["Type"] == "Expense"
        ).any():

            st.plotly_chart(
                top_spending_categories(monthly_df),
                use_container_width=True
            )

        else:
            st.info("No spending categories available.")

        st.divider()

        # -----------------------------------------
        # 10. TRANSACTION SUMMARY
        # -----------------------------------------

        st.subheader(
            f"Transactions - {selected_month}"
        )

        if not summary["transactions"].empty:

            display_df = summary["transactions"].copy()

            display_df["Date"] = (
                display_df["Date"].dt.strftime("%d-%b-%Y")
            )

            st.dataframe(
                display_df[
                    [
                        "Date",
                        "Type",
                        "Category",
                        "Description",
                        "Amount",
                        "Running Balance"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No transactions found for this month.")

    except Exception as error:

        st.error(
            f"Unable to load dashboard: {error}"
        )


elif page == "Transaction History":

    st.header("Transaction History")

    try:

        df = get_transactions(
            service,
            SPREADSHEET_ID
        )

        if df.empty:

            st.info("No transactions available.")
            st.stop()

        # Convert fields for filtering and display
        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

        df["Amount"] = pd.to_numeric(
            df["Amount"],
            errors="coerce"
        )

        df = df.dropna(
            subset=["Date", "Amount"]
        ).copy()

        # Summary metrics
        total_income = df.loc[
            df["Type"] == "Income", "Amount"
        ].sum()

        total_expenses = df.loc[
            df["Type"] == "Expense", "Amount"
        ].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("Transactions", len(df))
        col2.metric("Total Income", f"₹{total_income:,.2f}")
        col3.metric("Total Expenses", f"₹{total_expenses:,.2f}")

        st.divider()

        # Search
        search = st.text_input(
            "Search transactions",
            placeholder="Search description or category..."
        )

        col1, col2 = st.columns(2)

        with col1:
            type_filter = st.selectbox(
                "Transaction Type",
                ["All", "Income", "Expense"]
            )

        with col2:
            category_filter = st.selectbox(
                "Category",
                ["All"] + sorted(df["Category"].dropna().unique().tolist())
            )

        filtered = df.copy()

        if search:
            mask = (
                filtered["Description"].astype(str).str.contains(
                    search, case=False, na=False
                )
                |
                filtered["Category"].astype(str).str.contains(
                    search, case=False, na=False
                )
            )
            filtered = filtered[mask]

        if type_filter != "All":
            filtered = filtered[
                filtered["Type"] == type_filter
            ]

        if category_filter != "All":
            filtered = filtered[
                filtered["Category"] == category_filter
            ]

        filtered = filtered.sort_values(
            ["Date", "Sheet Row"],
            ascending=[False, False]
        )

        st.subheader("Transactions")

        display_df = filtered[
            [
                "Date",
                "Type",
                "Category",
                "Description",
                "Amount",
                "Payment Method"
            ]
        ].copy()

        display_df["Date"] = (
            display_df["Date"].dt.strftime("%d-%b-%Y")
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Edit / Delete selection
        st.subheader("Manage Transaction")

        if filtered.empty:

            st.info("No matching transactions found.")

        else:

            labels = {}

            for _, row in filtered.iterrows():

                label = (
                    f"Row {int(row['Sheet Row'])} | "
                    f"{row['Date'].strftime('%d-%b-%Y')} | "
                    f"{row['Type']} | "
                    f"{row['Description']} | "
                    f"₹{row['Amount']:,.2f}"
                )

                labels[label] = int(row["Sheet Row"])

            selected_label = st.selectbox(
                "Select a transaction",
                list(labels.keys())
            )

            selected_row = labels[selected_label]

            # Fetch fresh data before editing/deleting
            latest_df = get_transactions(
                service,
                SPREADSHEET_ID
            )

            selected_records = latest_df[
                latest_df["Sheet Row"] == selected_row
            ]

            if selected_records.empty:

                st.warning(
                    "This transaction has changed. "
                    "Refresh the page and try again."
                )

            else:

                record = selected_records.iloc[0]

                st.markdown("### Edit transaction")

                transaction_type = st.selectbox(
                    "Type",
                    ["Expense", "Income"],
                    index=(
                        0 if record["Type"] == "Expense" else 1
                    ),
                    key="edit_type"
                )

                available_categories = (
                    settings["expense_categories"]
                    if transaction_type == "Expense"
                    else settings["income_sources"]
                )

                if record["Category"] not in available_categories:
                    available_categories = (
                        available_categories + [record["Category"]]
                    )

                category = st.selectbox(
                    "Category / Income Source",
                    available_categories,
                    index=available_categories.index(
                        record["Category"]
                    ),
                    key="edit_category"
                )

                if record["Payment Method"] not in settings["payment_methods"]:
                    payment_options = (
                        settings["payment_methods"]
                        + [record["Payment Method"]]
                    )
                else:
                    payment_options = settings["payment_methods"]

                transaction_date = pd.to_datetime(
                    record["Date"]
                ).date()

                with st.form("edit_transaction_form"):

                    new_date = st.date_input(
                        "Date",
                        value=transaction_date
                    )

                    new_description = st.text_input(
                        "Description",
                        value=record["Description"]
                    )

                    new_amount = st.number_input(
                        "Amount (₹)",
                        min_value=0.01,
                        value=float(record["Amount"]),
                        step=10.0
                    )

                    new_payment = st.selectbox(
                        "Payment Method",
                        payment_options,
                        index=payment_options.index(
                            record["Payment Method"]
                        )
                    )

                    new_notes = st.text_area(
                        "Notes",
                        value=record["Notes"]
                    )

                    save_changes = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True
                    )

                if save_changes:

                    if not new_description.strip():
                        st.error("Description cannot be empty.")

                    else:

                        try:

                            # Check that the selected row still
                            # contains the same transaction.
                            verification = get_transactions(
                                service,
                                SPREADSHEET_ID
                            )

                            current = verification[
                                verification["Sheet Row"] == selected_row
                            ]

                            if current.empty:
                                st.error(
                                    "Transaction row no longer exists. "
                                    "Refresh and try again."
                                )

                            else:
                                current_record = current.iloc[0]

                                if (
                                    current_record["Date"] != record["Date"]
                                    or current_record["Description"] != record["Description"]
                                    or current_record["Amount"] != record["Amount"]
                                ):
                                    st.error(
                                        "Transaction changed since selection. "
                                        "Refresh and select it again."
                                    )

                                else:

                                    update_transaction(
                                        service=service,
                                        spreadsheet_id=SPREADSHEET_ID,
                                        row_number=selected_row,
                                        transaction_date=new_date,
                                        transaction_type=transaction_type,
                                        category=category,
                                        description=new_description,
                                        amount=new_amount,
                                        payment_method=new_payment,
                                        notes=new_notes
                                    )

                                    st.success(
                                        "Transaction updated successfully!"
                                    )

                                    st.rerun()

                        except Exception as error:
                            st.error(f"Update failed: {error}")

                st.divider()

                st.markdown("### Delete transaction")

                confirm_delete = st.checkbox(
                    "I confirm that I want to permanently delete this transaction.",
                    key="confirm_delete"
                )

                if st.button(
                    "Delete Transaction",
                    type="primary",
                    disabled=not confirm_delete
                ):

                    try:

                        # Re-read before deletion to check the row.
                        verification = get_transactions(
                            service,
                            SPREADSHEET_ID
                        )

                        current = verification[
                            verification["Sheet Row"] == selected_row
                        ]

                        if current.empty:
                            st.error(
                                "Transaction no longer exists. Refresh first."
                            )

                        else:

                            current_record = current.iloc[0]

                            if (
                                current_record["Date"] != record["Date"]
                                or current_record["Description"] != record["Description"]
                                or current_record["Amount"] != record["Amount"]
                            ):
                                st.error(
                                    "Transaction changed. Refresh before deleting."
                                )

                            else:

                                delete_transaction(
                                    service,
                                    SPREADSHEET_ID,
                                    selected_row
                                )

                                st.success(
                                    "Transaction deleted successfully!"
                                )

                                st.rerun()

                    except Exception as error:
                        st.error(f"Deletion failed: {error}")

    except Exception as error:

        st.error(
            f"Unable to retrieve transaction history: {error}"
        )



elif page == "Monthly Reports":

    st.header("Monthly Financial Reports")

    st.caption(
        "Select any month to view its financial position."
    )

    try:

        finance_data = get_financial_data(
            service,
            SPREADSHEET_ID
        )

        initial_balance = finance_data["initial_balance"]
        starting_date = finance_data["starting_date"]
        transactions = finance_data["transactions"]

        # Select any month, including future months
        selected_date = st.date_input(
            "Select reporting month",
            value=date.today(),
            min_value=pd.Timestamp(starting_date).date()
        )

        # Normalize selected date to the first day
        # of the selected month
        selected_month = date(
            selected_date.year,
            selected_date.month,
            1
        )

        # Calculate monthly financial position
        report = calculate_monthly_summary(
            transactions,
            initial_balance,
            starting_date,
            selected_month
        )

        st.divider()

        st.subheader(
            selected_month.strftime("%B %Y")
        )

        # Financial metrics
        col1, col2 = st.columns(2)

        col1.metric(
            "Opening Balance",
            f"₹{report['opening_balance']:,.2f}"
        )

        col2.metric(
            "Closing Balance",
            f"₹{report['closing_balance']:,.2f}"
        )

        col3, col4 = st.columns(2)

        col3.metric(
            "Total Income",
            f"₹{report['total_income']:,.2f}"
        )

        col4.metric(
            "Total Expenses",
            f"₹{report['total_expenses']:,.2f}"
        )

        st.divider()

        # Monthly transaction records
        st.subheader("Monthly Transactions")

        monthly_transactions = report["transactions"]

        if not monthly_transactions.empty:

            display_df = monthly_transactions.copy()

            display_df["Date"] = (
                display_df["Date"].dt.strftime("%d-%b-%Y")
            )

            st.dataframe(
                display_df[
                    [
                        "Date",
                        "Type",
                        "Category",
                        "Description",
                        "Amount",
                        "Payment Method",
                        "Running Balance"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No transactions recorded for this month. "
                "The closing balance carries forward "
                "from previous months."
            )

        # Financial calculation verification
        st.divider()

        st.subheader("Balance Calculation")

        st.write(
            f"Opening Balance: ₹{report['opening_balance']:,.2f}"
        )

        st.write(
            f"Add Income: ₹{report['total_income']:,.2f}"
        )

        st.write(
            f"Less Expenses: ₹{report['total_expenses']:,.2f}"
        )

        st.success(
            f"Closing Balance: ₹{report['closing_balance']:,.2f}"
        )

    except Exception as error:

        st.error(
            f"Unable to generate monthly report: {error}"
        )


elif page == "Settings":

    st.header("Settings")

    st.subheader("Expense Categories")
    st.write(settings["expense_categories"])

    st.subheader("Income Sources")
    st.write(settings["income_sources"])

    st.subheader("Payment Methods")
    st.write(settings["payment_methods"])


# --------------------------------------------------
# SIDEBAR FOOTER
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.caption("Personal Money Manager v1.0")
