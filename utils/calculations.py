
import pandas as pd


def prepare_transactions(transactions):
    """Normalize transaction fields used by dashboard calculations."""
    if transactions is None or transactions.empty:
        return transactions.copy() if transactions is not None else pd.DataFrame()

    df = transactions.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Type"] = df["Type"].astype(str).str.strip().str.title()

    df = df.dropna(subset=["Date", "Amount"]).copy()
    df = df[df["Type"].isin(["Income", "Expense"])].copy()
    df["Created At"] = df["Created At"].fillna("").astype(str) if "Created At" in df else ""

    return df.sort_values(
        ["Date", "Created At"] if "Created At" in df else ["Date"],
        kind="stable"
    ).reset_index(drop=True)


def filter_transactions_by_period(transactions, start_date, end_date):
    """Return transactions in an inclusive date range."""
    df = prepare_transactions(transactions)
    if df.empty:
        return df

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    return df[(df["Date"] >= start) & (df["Date"] <= end)].copy()


def calculate_period_totals(transactions, start_date, end_date):
    """Calculate period income, expenses, and net savings."""
    df = filter_transactions_by_period(transactions, start_date, end_date)

    income = df.loc[df["Type"] == "Income", "Amount"].sum() if not df.empty else 0
    expenses = df.loc[df["Type"] == "Expense", "Amount"].sum() if not df.empty else 0

    return {
        "income": float(income),
        "expenses": float(expenses),
        "savings": float(income - expenses),
        "transactions": df
    }


def calculate_comparison(current_value, previous_value):
    """Return absolute and percentage change against a previous period."""
    current = float(current_value)
    previous = float(previous_value)
    absolute_change = current - previous

    if previous == 0:
        if current == 0:
            percentage_change = 0.0
            status = "unchanged"
        else:
            percentage_change = None
            status = "increased"
        return {
            "absolute_change": absolute_change,
            "percentage_change": percentage_change,
            "status": status
        }

    percentage_change = (absolute_change / abs(previous)) * 100
    status = "increased" if absolute_change > 0 else (
        "decreased" if absolute_change < 0 else "unchanged"
    )
    return {
        "absolute_change": absolute_change,
        "percentage_change": percentage_change,
        "status": status
    }


def calculate_current_balance(transactions, initial_balance, starting_date):
    """Calculate the latest overall balance from the account starting state."""
    df = calculate_running_balance(
        transactions,
        initial_balance,
        starting_date
    )
    if df.empty:
        return float(initial_balance)
    return float(df["Running Balance"].iloc[-1])


def calculate_running_balance(
    transactions,
    initial_balance,
    starting_date
):
    """
    Calculate chronological running balances.
    Income increases balance.
    Expenses decrease balance.
    """

    if transactions.empty:
        return transactions.copy()

    df = transactions.copy()

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

    df["Type"] = (
        df["Type"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    invalid_types = ~df["Type"].isin(
        ["Income", "Expense"]
    )

    if invalid_types.any():
        raise ValueError(
            "Found transactions with invalid types."
        )

    df["Created At"] = df["Created At"].fillna("").astype(str)

    # Keep original row order for transactions
    # having the same date and creation timestamp.
    df = df.sort_values(
        ["Date", "Created At"],
        kind="stable"
    ).reset_index(drop=True)

    start_date = pd.Timestamp(starting_date)

    # Ignore records before the configured starting date.
    df = df[df["Date"] >= start_date].copy()

    df["Net Amount"] = df.apply(
        lambda row: (
            row["Amount"]
            if row["Type"] == "Income"
            else -row["Amount"]
        ),
        axis=1
    )

    df["Running Balance"] = (
        initial_balance + df["Net Amount"].cumsum()
    )

    return df


def calculate_monthly_summary(
    transactions,
    initial_balance,
    starting_date,
    selected_month
):
    """
    Calculate monthly opening, income, expenses and closing.
    """

    start_date = pd.Timestamp(starting_date)

    month_start = pd.Timestamp(
        selected_month.year,
        selected_month.month,
        1
    )

    month_end = month_start + pd.offsets.MonthEnd(0)

    df = calculate_running_balance(
        transactions,
        initial_balance,
        start_date
    )

    previous = df[df["Date"] < month_start]

    monthly = df[
        (df["Date"] >= month_start) &
        (df["Date"] <= month_end)
    ].copy()

    opening_balance = (
        initial_balance + previous["Net Amount"].sum()
    )

    total_income = monthly.loc[
        monthly["Type"] == "Income",
        "Amount"
    ].sum()

    total_expenses = monthly.loc[
        monthly["Type"] == "Expense",
        "Amount"
    ].sum()

    closing_balance = (
        opening_balance + total_income - total_expenses
    )

    if not monthly.empty:
        monthly["Running Balance"] = (
            opening_balance + monthly["Net Amount"].cumsum()
        )

    return {
        "opening_balance": opening_balance,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "closing_balance": closing_balance,
        "transactions": monthly
    }
