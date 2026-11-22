
import pandas as pd


def get_financial_data(service, spreadsheet_id):

    # Retrieve account settings
    account_response = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="'Account'!A1:B5"
    ).execute()

    account_rows = account_response.get("values", [])

    account = {
        row[0]: row[1]
        for row in account_rows[1:]
        if len(row) >= 2
    }

    initial_balance = float(
        account["Initial Balance"]
    )

    starting_date = account["Starting Date"]

    # Retrieve transactions
    transaction_response = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="'Transactions'!A1:H"
    ).execute()

    rows = transaction_response.get("values", [])

    headers = rows[0] if rows else []

    records = rows[1:] if len(rows) > 1 else []

    transactions = pd.DataFrame(
        records,
        columns=headers
    )

    expected_columns = [
        "Date",
        "Type",
        "Category",
        "Description",
        "Amount",
        "Payment Method",
        "Created At",
        "Notes"
    ]

    if transactions.empty:
        transactions = pd.DataFrame(
            columns=expected_columns
        )

    return {
        "initial_balance": initial_balance,
        "starting_date": starting_date,
        "transactions": transactions,
        "currency": account.get("Currency", "INR")
    }
