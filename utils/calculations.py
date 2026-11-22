
import pandas as pd


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
