import pandas as pd

from utils.calculations import (
    calculate_comparison,
    calculate_current_balance,
    calculate_period_totals,
    filter_transactions_by_period
)
from services.visualization_service import (
    period_income_expense_chart,
    expense_category_donut_chart,
    period_daily_expense_chart
)


transactions = pd.DataFrame([
    {"Date": "2026-10-31", "Type": "Expense", "Category": "Food", "Description": "Old", "Amount": 100, "Created At": "2026-10-31T10:00:00"},
    {"Date": "2026-11-01", "Type": "Income", "Category": "Salary", "Description": "Salary", "Amount": 1000, "Created At": "2026-11-01T10:00:00"},
    {"Date": "2026-11-05", "Type": "Expense", "Category": "Food", "Description": "Lunch", "Amount": 200, "Created At": "2026-11-05T10:00:00"},
    {"Date": "2026-11-10", "Type": "Expense", "Category": "Travel", "Description": "Train", "Amount": 300, "Created At": "2026-11-10T10:00:00"},
    {"Date": "2026-11-11", "Type": "Income", "Category": "Freelance", "Description": "Project", "Amount": 400, "Created At": "2026-11-11T10:00:00"},
])


def test_monthly_filter():
    period = filter_transactions_by_period(
        transactions,
        "2026-11-01",
        "2026-11-30"
    )
    assert len(period) == 4
    summary = calculate_period_totals(period, "2026-11-01", "2026-11-30")
    assert summary["income"] == 1400
    assert summary["expenses"] == 500
    assert summary["savings"] == 900


def test_weekly_monday_sunday_filter():
    period = filter_transactions_by_period(
        transactions,
        "2026-11-09",
        "2026-11-15"
    )
    assert len(period) == 2
    assert set(period["Description"]) == {"Train", "Project"}


def test_custom_range_and_previous_period():
    period = calculate_period_totals(
        transactions,
        "2026-11-01",
        "2026-11-10"
    )
    previous = calculate_period_totals(
        transactions,
        "2026-10-22",
        "2026-10-31"
    )
    assert period["income"] == 1000
    assert period["expenses"] == 500
    assert previous["expenses"] == 100


def test_zero_previous_comparison():
    comparison = calculate_comparison(250, 0)
    assert comparison["percentage_change"] is None
    assert comparison["status"] == "increased"
    assert calculate_comparison(0, 0)["status"] == "unchanged"


def test_current_balance_ignores_period():
    balance = calculate_current_balance(
        transactions,
        initial_balance=5000,
        starting_date="2026-10-01"
    )
    assert balance == 5800


def test_empty_period_and_charts():
    empty = calculate_period_totals(
        transactions,
        "2027-01-01",
        "2027-01-31"
    )
    assert empty["income"] == 0
    assert empty["expenses"] == 0
    assert empty["savings"] == 0
    assert empty["transactions"].empty

    assert period_income_expense_chart(
        transactions, "2026-11-01", "2026-11-30", "Monthly"
    ) is not None
    assert expense_category_donut_chart(
        transactions, "2026-11-01", "2026-11-30"
    ) is not None
    assert period_daily_expense_chart(
        transactions, "2026-11-01", "2026-11-10"
    ) is not None


if __name__ == "__main__":
    test_monthly_filter()
    test_weekly_monday_sunday_filter()
    test_custom_range_and_previous_period()
    test_zero_previous_comparison()
    test_current_balance_ignores_period()
    test_empty_period_and_charts()
    print("Dashboard calculation tests passed.")
