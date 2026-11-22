
import pandas as pd

from utils.calculations import calculate_running_balance

transactions = pd.DataFrame([
    {
        "Date": "2026-11-05",
        "Type": "Expense",
        "Amount": 200,
        "Created At": "2026-11-05T10:00:00"
    },
    {
        "Date": "2026-11-15",
        "Type": "Income",
        "Amount": 35000,
        "Created At": "2026-11-15T10:00:00"
    },
    {
        "Date": "2026-11-20",
        "Type": "Expense",
        "Amount": 500,
        "Created At": "2026-11-20T10:00:00"
    }
])

result = calculate_running_balance(
    transactions,
    initial_balance=53491,
    starting_date="2026-11-01"
)

print(
    result[
        ["Date", "Type", "Amount", "Running Balance"]
    ].to_string(index=False)
)

print(
    "\nFinal balance:",
    result["Running Balance"].iloc[-1]
)
