
import os
import streamlit as st
import pandas as pd

from dotenv import load_dotenv
from googleapiclient.errors import HttpError

from services.google_sheets import get_google_sheets_service
from services.settings_service import get_settings, add_setting_value
from services.transaction_service import add_transaction
from datetime import date, datetime
from utils.calculations import (
    calculate_monthly_summary,
    calculate_period_totals,
    calculate_comparison,
    calculate_current_balance,
    prepare_transactions
)
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
    top_spending_categories,
    period_income_expense_chart,
    expense_category_donut_chart,
    period_daily_expense_chart
)

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

if not SPREADSHEET_ID:
    try:
        SPREADSHEET_ID = st.secrets["SPREADSHEET_ID"]
    except (KeyError, FileNotFoundError):
        SPREADSHEET_ID = None

st.set_page_config(
    page_title="Personal Money Manager",
    page_icon="💰",
    layout="wide"
)

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background: #F8FAFC;
        border-right: 1px solid #E5E7EB;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #475569;
    }
    section[data-testid="stSidebar"] [data-testid="stRadio"] {
        padding: 0.25rem 0.65rem 0 0.65rem;
    }
    section[data-testid="stSidebar"] [role="radiogroup"] label {
        border: 1px solid transparent;
        border-radius: 9px;
        margin: 0.08rem 0;
        padding: 0.52rem 0.65rem;
        transition: background 0.15s ease, border-color 0.15s ease;
    }
    section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: #EEF2FF;
        border-color: #E0E7FF;
    }
    section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: #FFFFFF;
        border-color: #DDE5F0;
        box-shadow: 0 1px 4px rgba(15, 23, 42, 0.08);
    }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0.15rem 0.65rem 0.75rem 0.65rem;
        padding: 0.75rem;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        background: #FFFFFF;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .sidebar-brand-icon {
        display: grid;
        place-items: center;
        width: 36px;
        height: 36px;
        flex: 0 0 36px;
        border-radius: 10px;
        background: #EEF2FF;
        font-size: 1.15rem;
    }
    .sidebar-brand-title {
        color: #1F2937;
        font-size: 0.92rem;
        font-weight: 750;
        line-height: 1.15;
    }
    .sidebar-brand-subtitle {
        color: #94A3B8;
        font-size: 0.72rem;
        margin-top: 3px;
    }
    .kpi-card {
        min-height: 118px;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        background: #FFFFFF;
        padding: 14px 16px 12px 16px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    }
    .kpi-label {
        color: #667085;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .kpi-value {
        color: #18181B;
        font-size: 1.55rem;
        font-weight: 750;
        line-height: 1.15;
        margin-bottom: 10px;
    }
    .kpi-comparison {
        color: #667085;
        font-size: 0.76rem;
        line-height: 1.25;
        min-height: 19px;
    }
    .kpi-income {
        border-top: 3px solid #16A34A;
    }
    .kpi-expense {
        border-top: 3px solid #DC2626;
    }
    .kpi-neutral {
        border-top: 3px solid #3B82F6;
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 95% 0%, rgba(219, 234, 254, 0.48), transparent 25rem),
            #F7F9FC;
    }
    [data-testid="stMain"] .block-container {
        padding-top: 1.35rem;
        padding-bottom: 2rem;
    }
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3 {
        color: #172554;
        letter-spacing: -0.025em;
    }
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3 {
        margin-top: 0.6rem;
    }
    [data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #E5EAF2;
        border-radius: 14px;
    }
    [data-testid="stMain"] [data-testid="stTextInput"] input,
    [data-testid="stMain"] [data-testid="stNumberInput"] input,
    [data-testid="stMain"] [data-testid="stDateInput"] input,
    [data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border-radius: 9px;
        border-color: #D8E0EC;
        background: #FFFFFF;
    }
    [data-testid="stMain"] [data-testid="stTextInput"] input:focus,
    [data-testid="stMain"] [data-testid="stNumberInput"] input:focus,
    [data-testid="stMain"] [data-testid="stDateInput"] input:focus {
        border-color: #6366F1;
        box-shadow: 0 0 0 1px #6366F1;
    }
    [data-testid="stMain"] .stButton > button,
    [data-testid="stMain"] [data-testid="stFormSubmitButton"] button {
        border-radius: 9px;
        border: 1px solid #D9E1EF;
        font-weight: 600;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    [data-testid="stMain"] .stButton > button:hover,
    [data-testid="stMain"] [data-testid="stFormSubmitButton"] button:hover {
        border-color: #A5B4FC;
        color: #4338CA;
        box-shadow: 0 3px 10px rgba(67, 56, 202, 0.12);
        transform: translateY(-1px);
    }
    [data-testid="stMain"] [data-testid="stDataFrame"] {
        border: 1px solid #E5EAF2;
        border-radius: 12px;
        overflow: hidden;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F0F5FF 0%, #F8FAFC 42%, #F8FAFC 100%);
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# GOOGLE SHEETS CONNECTION
# --------------------------------------------------

@st.cache_resource
def connect_google_sheets():
    return get_google_sheets_service()


@st.cache_data(ttl=30, show_spinner="Loading settings...")
def load_settings(spreadsheet_id):
    return get_settings(connect_google_sheets(), spreadsheet_id)


@st.cache_data(ttl=30, show_spinner="Loading financial data...")
def load_financial_data(spreadsheet_id):
    return get_financial_data(connect_google_sheets(), spreadsheet_id)


@st.cache_data(ttl=15, show_spinner="Loading transactions...")
def load_transactions(spreadsheet_id):
    return get_transactions(connect_google_sheets(), spreadsheet_id)


def clear_sheet_data_cache():
    load_settings.clear()
    load_financial_data.clear()
    load_transactions.clear()


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

if not SPREADSHEET_ID:
    st.error("SPREADSHEET_ID is missing from .env")
    st.stop()

try:
    service = connect_google_sheets()
    settings = load_settings(SPREADSHEET_ID)

except Exception as error:
    st.error(f"Unable to connect to Google Sheets: {error}")
    st.stop()


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">₹</div>
        <div>
            <div class="sidebar-brand-title">Personal Finance</div>
            <div class="sidebar-brand-subtitle">Money dashboard</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Transaction",
        "Transaction History",
        "Monthly Reports",
        "Settings"
    ],
    key="navigation",
    label_visibility="collapsed"
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

    st.markdown(
        """
        <style>
        div[data-testid="stForm"] {
            padding: 1rem 1.15rem 0.8rem 1.15rem;
            border: 1px solid #E5E7EB;
            border-radius: 14px;
            background: #FFFFFF;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
        }
        div[data-testid="stForm"] [data-testid="stWidgetLabel"] {
            padding-bottom: 0.2rem;
        }
        div[data-testid="stForm"] [data-testid="stFormSubmitButton"] {
            margin-top: 0.15rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.form("transaction_form"):
        date_col, category_col = st.columns(2)
        with date_col:
            transaction_date = st.date_input("Transaction Date")
        with category_col:
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

        amount_col, payment_col = st.columns(2)
        with amount_col:
            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=10.0,
                format="%.2f"
            )
        with payment_col:
            payment_method = st.selectbox(
                "Payment Method",
                settings["payment_methods"]
            )

        description_col, notes_col = st.columns(2)
        with description_col:
            description = st.text_input(
                "Description (Optional)",
                placeholder="e.g. Lunch, Monthly salary"
            )
        with notes_col:
            notes = st.text_input(
                "Notes (Optional)",
                placeholder="Add a note"
            )

        submitted = st.form_submit_button(
            "Save Transaction",
            width="stretch"
        )

        if submitted:

            if amount <= 0:
                st.error("Please enter an amount greater than zero.")

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
                    clear_sheet_data_cache()

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
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 0.75rem;
            padding-bottom: 0.75rem;
        }
        h1 {
            margin-top: 0 !important;
            margin-bottom: 0.35rem !important;
        }
        [data-testid="stCaptionContainer"] {
            margin-top: 0.15rem;
        }
        hr {
            margin-top: 0.45rem !important;
            margin-bottom: 0.45rem !important;
        }
        [data-testid="stRadio"] {
            margin-bottom: -0.35rem;
        }
        [data-testid="stSelectbox"],
        [data-testid="stDateInput"] {
            margin-bottom: -0.15rem;
        }
        @media (max-width: 640px) {
            .block-container {
                padding-top: 0.5rem;
                padding-left: 0.75rem;
                padding-right: 0.75rem;
            }
            .kpi-card {
                min-height: 132px;
                padding: 12px;
            }
            .kpi-value {
                font-size: 1.25rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.header("Financial Dashboard")

    try:
        finance_data = load_financial_data(SPREADSHEET_ID)
        initial_balance = finance_data["initial_balance"]
        starting_date = finance_data["starting_date"]
        df = prepare_transactions(finance_data["transactions"])
        df = df[df["Date"] >= pd.Timestamp(starting_date)].copy()

        period_mode = st.radio(
            "Dashboard period",
            ["Monthly", "Weekly", "Daily", "Custom Date Range"],
            horizontal=True
        )

        today = date.today()

        if period_mode == "Monthly":
            month_col, year_col = st.columns(2)
            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            start_year = pd.Timestamp(starting_date).year
            year_options = list(range(start_year, today.year + 2))

            with month_col:
                selected_month_name = st.selectbox(
                    "Month",
                    month_names,
                    index=today.month - 1
                )
            with year_col:
                selected_year = st.selectbox(
                    "Year",
                    year_options,
                    index=year_options.index(today.year)
                )

            selected_month_number = month_names.index(selected_month_name) + 1
            period_start = pd.Timestamp(selected_year, selected_month_number, 1)
            period_end = period_start + pd.offsets.MonthEnd(0)
            previous_start = (period_start - pd.offsets.MonthBegin(1)).normalize()
            previous_end = period_start - pd.Timedelta(days=1)

        elif period_mode == "Weekly":
            week_col, nav_col = st.columns([3, 1])
            if "dashboard_week" not in st.session_state:
                st.session_state.dashboard_week = today

            with week_col:
                chosen_week_date = st.date_input(
                    "Week containing",
                    value=st.session_state.dashboard_week
                )
            if chosen_week_date != st.session_state.dashboard_week:
                st.session_state.dashboard_week = chosen_week_date
            with nav_col:
                previous_week = st.button("Previous week", width="stretch")
                next_week = st.button("Next week", width="stretch")

            if previous_week:
                st.session_state.dashboard_week = st.session_state.dashboard_week - pd.Timedelta(days=7)
                st.rerun()
            if next_week:
                st.session_state.dashboard_week = st.session_state.dashboard_week + pd.Timedelta(days=7)
                st.rerun()

            chosen_week_date = st.session_state.dashboard_week
            chosen = pd.Timestamp(chosen_week_date)
            period_start = (chosen - pd.Timedelta(days=chosen.weekday())).normalize()
            period_end = period_start + pd.Timedelta(days=6)
            previous_start = period_start - pd.Timedelta(days=7)
            previous_end = period_start - pd.Timedelta(days=1)

        elif period_mode == "Daily":
            selected_day = st.date_input(
                "Select date",
                value=today
            )
            period_start = pd.Timestamp(selected_day)
            period_end = period_start
            previous_start = period_start - pd.Timedelta(days=1)
            previous_end = previous_start

        else:
            custom_col1, custom_col2 = st.columns(2)
            with custom_col1:
                custom_start = st.date_input(
                    "Start date",
                    value=today - pd.Timedelta(days=6)
                )
            with custom_col2:
                custom_end = st.date_input(
                    "End date",
                    value=today
                )

            if custom_end < custom_start:
                st.error("End date cannot be earlier than start date.")
                st.stop()

            period_start = pd.Timestamp(custom_start)
            period_end = pd.Timestamp(custom_end)
            duration_days = (period_end - period_start).days + 1
            previous_end = period_start - pd.Timedelta(days=1)
            previous_start = previous_end - pd.Timedelta(days=duration_days - 1)

        period_summary = calculate_period_totals(
            df,
            period_start,
            period_end
        )
        previous_summary = calculate_period_totals(
            df,
            previous_start,
            previous_end
        )

        current_balance = calculate_current_balance(
            df,
            initial_balance,
            starting_date
        )

        income_comparison = calculate_comparison(
            period_summary["income"],
            previous_summary["income"]
        )
        expense_comparison = calculate_comparison(
            period_summary["expenses"],
            previous_summary["expenses"]
        )

        def comparison_text(comparison, label):
            absolute = comparison["absolute_change"]
            percentage = comparison["percentage_change"]
            status = comparison["status"]
            if percentage is None:
                detail = f"New compared with previous period (₹{absolute:,.2f})"
            else:
                detail = f"{status.title()} {abs(percentage):.1f}% (₹{absolute:+,.2f})"
            return f"{label}: {detail}"

        kpi1, kpi2, kpi3 = st.columns(3)

        with kpi1:
            st.markdown(
                f"""
                <div class="kpi-card kpi-neutral">
                    <div class="kpi-label">Current Balance</div>
                    <div class="kpi-value">₹{current_balance:,.2f}</div>
                    <div class="kpi-comparison">Overall balance; unchanged by period</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with kpi2:
            st.markdown(
                f"""
                <div class="kpi-card kpi-income">
                    <div class="kpi-label">Total Income</div>
                    <div class="kpi-value">₹{period_summary['income']:,.2f}</div>
                    <div class="kpi-comparison">{comparison_text(income_comparison, "Income")}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with kpi3:
            st.markdown(
                f"""
                <div class="kpi-card kpi-expense">
                    <div class="kpi-label">Total Expenses</div>
                    <div class="kpi-value">₹{period_summary['expenses']:,.2f}</div>
                    <div class="kpi-comparison">{comparison_text(expense_comparison, "Expenses")}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.divider()
        st.subheader("Income vs Expenses")
        st.plotly_chart(
            period_income_expense_chart(
                df,
                period_start,
                period_end,
                period_mode
            ),
            width="stretch"
        )

        st.divider()
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("Expense Distribution")
            donut = expense_category_donut_chart(
                df,
                period_start,
                period_end
            )
            if donut is None:
                st.info("No expenses recorded for this period.")
            else:
                st.plotly_chart(donut, width="stretch")

        with chart_col2:
            st.subheader("Daily Spending Trend")
            st.plotly_chart(
                period_daily_expense_chart(
                    df,
                    period_start,
                    period_end
                ),
                width="stretch"
            )

    except Exception as error:
        st.error(f"Unable to load dashboard: {error}")


elif page == "Transaction History":

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 0.75rem;
            padding-bottom: 0.75rem;
        }
        h1 {
            margin-top: 0 !important;
            margin-bottom: 0.35rem !important;
        }
        hr {
            margin-top: 0.45rem !important;
            margin-bottom: 0.45rem !important;
        }
        .history-kpi-card {
            min-height: 118px;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            background: #FFFFFF;
            padding: 14px 16px 12px 16px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
        }
        .history-kpi-label {
            color: #667085;
            font-size: 0.82rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .history-kpi-value {
            color: #18181B;
            font-size: 1.55rem;
            font-weight: 750;
            line-height: 1.15;
        }
        .history-kpi-income {
            border-top: 3px solid #16A34A;
        }
        .history-kpi-expense {
            border-top: 3px solid #DC2626;
        }
        .history-kpi-count {
            border-top: 3px solid #3B82F6;
        }
        @media (max-width: 640px) {
            .block-container {
                padding-top: 0.5rem;
                padding-left: 0.75rem;
                padding-right: 0.75rem;
            }
            .history-kpi-card {
                min-height: 105px;
                padding: 12px;
            }
            .history-kpi-value {
                font-size: 1.2rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.header("Transaction History")
    st.caption("Search, review, and manage your transactions.")

    try:

        df = load_transactions(SPREADSHEET_ID)

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

        metric_columns = st.columns(3)
        history_metrics = [
            ("Transactions", f"{len(df):,}", "history-kpi-count"),
            ("Total Income", f"₹{total_income:,.2f}", "history-kpi-income"),
            ("Total Expenses", f"₹{total_expenses:,.2f}", "history-kpi-expense")
        ]
        for column, (label, value, accent) in zip(metric_columns, history_metrics):
            with column:
                st.markdown(
                    f"""
                    <div class="history-kpi-card {accent}">
                        <div class="history-kpi-label">{label}</div>
                        <div class="history-kpi-value">{value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.divider()

        search_col, type_col, category_col = st.columns([1.5, 1, 1])
        with search_col:
            search = st.text_input(
                "Search transactions",
                placeholder="Description or category..."
            )
        with type_col:
            type_filter = st.selectbox(
                "Transaction Type",
                ["All", "Income", "Expense"]
            )
        with category_col:
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

        st.subheader("Manage Transaction")

        if filtered.empty:

            st.info("No matching transactions found.")

        else:

            labels = {}

            for _, row in filtered.iterrows():

                description_label = str(row["Description"]).strip()
                if not description_label:
                    description_label = "(No description)"

                label = (
                    f"Row {int(row['Sheet Row'])} | "
                    f"{row['Date'].strftime('%d-%b-%Y')} | "
                    f"{row['Type']} | "
                    f"{description_label} | "
                    f"₹{row['Amount']:,.2f}"
                )

                labels[label] = int(row["Sheet Row"])

            selected_label = st.selectbox(
                "Select a transaction to update or delete",
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

                st.markdown("### Update Transaction")

                type_col, category_col = st.columns(2)
                with type_col:
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

                with category_col:
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
                    date_col, description_col = st.columns(2)
                    with date_col:
                        new_date = st.date_input(
                            "Date",
                            value=transaction_date
                        )
                    with description_col:
                        new_description = st.text_input(
                            "Description (Optional)",
                            value=record["Description"]
                        )

                    amount_col, payment_col = st.columns(2)
                    with amount_col:
                        new_amount = st.number_input(
                            "Amount (₹)",
                            min_value=0.01,
                            value=float(record["Amount"]),
                            step=10.0
                        )
                    with payment_col:
                        new_payment = st.selectbox(
                            "Payment Method",
                            payment_options,
                            index=payment_options.index(
                                record["Payment Method"]
                            )
                        )

                    notes_col, save_col = st.columns(2)
                    with notes_col:
                        new_notes = st.text_input(
                            "Notes (Optional)",
                            value=record["Notes"]
                        )
                    with save_col:
                        st.write("")
                        save_changes = st.form_submit_button(
                            "Save Changes",
                            width="stretch"
                        )

                if save_changes:
                    try:

                        # Re-read to detect changes since selection.
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
                                    description=new_description.strip(),
                                    amount=new_amount,
                                    payment_method=new_payment,
                                    notes=new_notes
                                )
                                clear_sheet_data_cache()

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
                                clear_sheet_data_cache()

                                st.success(
                                    "Transaction deleted successfully!"
                                )

                                st.rerun()

                    except Exception as error:
                        st.error(f"Deletion failed: {error}")

        st.divider()
        st.subheader("Latest 10 Transactions")

        recent_transactions = filtered.head(10)
        if recent_transactions.empty:
            st.info("No matching transactions found.")
        else:
            display_df = recent_transactions[
                [
                    "Date",
                    "Type",
                    "Category",
                    "Description",
                    "Amount",
                    "Payment Method"
                ]
            ].copy()
            display_df["Date"] = display_df["Date"].dt.strftime("%d-%b-%Y")
            st.dataframe(
                display_df,
                width="stretch",
                hide_index=True
            )

    except Exception as error:

        st.error(
            f"Unable to retrieve transaction history: {error}"
        )



elif page == "Monthly Reports":

    st.markdown(
        """
        <style>
        .report-kpi-grid {
            margin-top: 0.35rem;
            margin-bottom: 0.8rem;
        }
        .report-kpi {
            min-height: 108px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.header("Monthly Financial Reports")

    st.caption(
        "Select any month to view its financial position."
    )

    try:

        finance_data = load_financial_data(SPREADSHEET_ID)

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

        st.subheader(
            selected_month.strftime("%B %Y")
        )

        report_kpis = [
            ("Opening Balance", report["opening_balance"], "kpi-neutral"),
            ("Closing Balance", report["closing_balance"], "kpi-neutral"),
            ("Total Income", report["total_income"], "kpi-income"),
            ("Total Expenses", report["total_expenses"], "kpi-expense")
        ]
        kpi_columns = st.columns(4)
        for column, (label, amount, accent) in zip(kpi_columns, report_kpis):
            with column:
                st.markdown(
                    f"""
                    <div class="kpi-card report-kpi {accent}">
                        <div class="kpi-label">{label}</div>
                        <div class="kpi-value">₹{amount:,.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
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
                width="stretch",
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
    st.caption("Add options here to make them available in transaction forms.")

    setting_sections = [
        ("Expense Categories", "expense_categories", "category"),
        ("Income Sources", "income_sources", "income source"),
        ("Payment Methods", "payment_methods", "payment method")
    ]
    setting_tabs = st.tabs([section[0] for section in setting_sections])

    for tab, (title, setting_key, input_label) in zip(setting_tabs, setting_sections):
        with tab:
            st.subheader(title)
            current_values = settings[setting_key]

            if current_values:
                st.caption(f"{len(current_values)} available")
                st.markdown("\n".join(f"- {value}" for value in current_values))
            else:
                st.info(f"No {title.lower()} have been added yet.")

            with st.form(f"add_{setting_key}_form", clear_on_submit=True):
                new_value = st.text_input(
                    f"New {input_label}",
                    placeholder=f"Enter a {input_label}"
                )
                add_submitted = st.form_submit_button(
                    f"Add {input_label.title()}",
                    width="stretch"
                )

            if add_submitted:
                try:
                    add_setting_value(
                        service,
                        SPREADSHEET_ID,
                        setting_key,
                        new_value
                    )
                    clear_sheet_data_cache()
                    st.success(f"{input_label.title()} added.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
                except HttpError as error:
                    st.error(f"Unable to update settings in Google Sheets: {error}")
                except Exception as error:
                    st.error(f"Unexpected error while updating settings: {error}")


# --------------------------------------------------
# SIDEBAR FOOTER
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.caption("Personal Money Manager • v1.0")
