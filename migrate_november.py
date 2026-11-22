
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from services.google_sheets import get_google_sheets_service

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

SOURCE_SHEET = "Nov 2026"
DESTINATION_SHEET = "Transactions"


def parse_date(value):

    if not value:
        return None

    formats = [
        "%d-%b-%Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(
                str(value).strip(), fmt
            ).strftime("%Y-%m-%d")
        except ValueError:
            continue

    raise ValueError(f"Unrecognised date: {value}")


def migrate_november():

    service = get_google_sheets_service()

    # Check migration status
    account = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Account'!A1:B5"
    ).execute().get("values", [])

    status = next(
        (
            row[1] for row in account
            if len(row) > 1
            and row[0] == "November Migration Status"
        ),
        None
    )

    if status == "Completed":
        print("November migration already completed.")
        return

    if status != "Pending":
        raise ValueError(
            "Account migration status is missing or invalid."
        )

    # Ensure destination contains only its header
    existing = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Transactions'!A2:H"
    ).execute().get("values", [])

    if existing:
        raise ValueError(
            "Transactions already contains data. "
            "Please inspect it before migration."
        )

    # Read November expense data: E through H
    expenses = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Nov 2026'!E9:H100"
    ).execute().get("values", [])

    # Read payment methods from J
    payments = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Nov 2026'!J9:J100"
    ).execute().get("values", [])

    records = []

    created_at = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    for index, row in enumerate(expenses):

        row = row + [""] * (4 - len(row))

        date, category, description, amount = row

        if not date or not amount:
            continue

        amount = float(str(amount).replace(",", ""))

        if amount <= 0:
            continue

        payment_method = (
            payments[index][0]
            if index < len(payments) and payments[index]
            else ""
        )

        records.append([
            parse_date(date),
            "Expense",
            category,
            description,
            amount,
            payment_method,
            created_at,
            "Migrated from November 2026"
        ])

    if len(records) != 10:
        raise ValueError(
            f"Expected 10 expense records, found {len(records)}. "
            "Migration stopped without writing."
        )

    total_expenses = sum(
        float(record[4]) for record in records
    )

    expected_balance = 53491 - total_expenses

    if total_expenses != 699 or expected_balance != 52792:
        raise ValueError(
            "Financial validation failed. Migration stopped."
        )

    # Write transactions and migration status together
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {
                    "range": "'Transactions'!A2:H11",
                    "values": records
                },
                {
                    "range": "'Account'!B5",
                    "values": [["Completed"]]
                }
            ]
        }
    ).execute()

    print("\nNovember migration successful!")
    print("Transactions migrated:", len(records))
    print("Total expenses: ₹", total_expenses)
    print("Opening balance: ₹53,491")
    print("Closing balance: ₹", expected_balance)


if __name__ == "__main__":
    migrate_november()
