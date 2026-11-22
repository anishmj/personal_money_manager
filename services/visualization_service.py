
import plotly.express as px
import pandas as pd


def income_expense_chart(df):

    monthly = df.copy()

    monthly["Month"] = monthly["Date"].dt.to_period(
        "M"
    ).astype(str)

    summary = (
        monthly.groupby(["Month", "Type"])["Amount"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        summary,
        x="Month",
        y="Amount",
        color="Type",
        barmode="group",
        title="Monthly Income vs Expenses",
        text_auto=".2s"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Amount (INR)"
    )

    return fig


def category_expense_chart(df):

    expenses = df[
        df["Type"] == "Expense"
    ]

    summary = (
        expenses.groupby("Category")["Amount"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        summary,
        names="Category",
        values="Amount",
        hole=0.45,
        title="Category-wise Spending"
    )

    return fig


def daily_expense_chart(df):

    expenses = df[
        df["Type"] == "Expense"
    ].copy()

    daily = (
        expenses.groupby(
            expenses["Date"].dt.date
        )["Amount"]
        .sum()
        .reset_index()
    )

    fig = px.line(
        daily,
        x="Date",
        y="Amount",
        markers=True,
        title="Daily Expense Trend"
    )

    return fig


def savings_trend_chart(df, initial_balance):

    data = df.copy()

    data["Net Amount"] = data.apply(
        lambda row: (
            row["Amount"]
            if row["Type"] == "Income"
            else -row["Amount"]
        ),
        axis=1
    )

    data = data.sort_values(
        ["Date", "Created At"],
        kind="stable"
    )

    data["Balance"] = (
        initial_balance + data["Net Amount"].cumsum()
    )

    fig = px.line(
        data,
        x="Date",
        y="Balance",
        markers=True,
        title="Balance Trend"
    )

    return fig


def top_spending_categories(df):

    expenses = df[
        df["Type"] == "Expense"
    ]

    summary = (
        expenses.groupby("Category")["Amount"]
        .sum()
        .reset_index()
        .sort_values("Amount", ascending=True)
        .tail(5)
    )

    fig = px.bar(
        summary,
        x="Amount",
        y="Category",
        orientation="h",
        title="Top 5 Spending Categories",
        text_auto=".2s"
    )

    return fig
