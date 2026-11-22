from datetime import datetime, timezone
import pandas as pd
TRANSACTION_HEADERS = [
    "Date",
    "Type",
    "Category",
    "Description",
    "Amount",
    "Payment Method",
    "Created At",
    "Notes"
]


def create_transactions_sheet(service, spreadsheet_id):

    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="sheets.properties"
    ).execute()

    existing_sheets = [
        sheet["properties"]["title"]
        for sheet in spreadsheet.get("sheets", [])
    ]

    if "Transactions" in existing_sheets:
        print("Transactions sheet already exists.")
        return

    request = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": "Transactions"
                    }
                }
            }
        ]
    }

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request
    ).execute()

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="'Transactions'!A1:H1",
        valueInputOption="RAW",
        body={"values": [TRANSACTION_HEADERS]}
    ).execute()

    print("Transactions worksheet created successfully!")





def add_transaction(
    service,
    spreadsheet_id,
    transaction_date,
    transaction_type,
    category,
    description,
    amount,
    payment_method,
    notes=""
):

    # Validate transaction amount
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    # Prepare timestamp
    created_at = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    # Prepare transaction record
    row = [
        transaction_date.isoformat(),
        transaction_type,
        category,
        description,
        float(amount),
        payment_method,
        created_at,
        notes
    ]

    # Save to Google Sheets
    response = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="'Transactions'!A:H",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={
            "values": [row]
        }
    ).execute()

    return response



def get_transactions(service, spreadsheet_id):

    response = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range="'Transactions'!A1:H"
    ).execute()

    rows = response.get("values", [])

    headers = rows[0] if rows else []

    records = rows[1:] if len(rows) > 1 else []

    columns = [
        "Date",
        "Type",
        "Category",
        "Description",
        "Amount",
        "Payment Method",
        "Created At",
        "Notes"
    ]

    transactions = []

    for row_number, row in enumerate(records, start=2):

        row = row + [""] * (8 - len(row))

        record = dict(zip(columns, row))

        record["Sheet Row"] = row_number

        transactions.append(record)

    return pd.DataFrame(transactions)


def update_transaction(
    service,
    spreadsheet_id,
    row_number,
    transaction_date,
    transaction_type,
    category,
    description,
    amount,
    payment_method,
    notes=""
):

    if row_number < 2:
        raise ValueError("Invalid transaction row.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    # Preserve the original creation timestamp
    existing = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"'Transactions'!G{row_number}"
    ).execute()

    created_at = (
        existing.get("values", [[""]])[0][0]
    )

    row = [
        transaction_date.isoformat(),
        transaction_type,
        category,
        description.strip(),
        float(amount),
        payment_method,
        created_at,
        notes.strip()
    ]

    return service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"'Transactions'!A{row_number}:H{row_number}",
        valueInputOption="USER_ENTERED",
        body={"values": [row]}
    ).execute()


def delete_transaction(
    service,
    spreadsheet_id,
    row_number
):

    if row_number < 2:
        raise ValueError("Invalid transaction row.")

    request = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": get_transactions_sheet_id(
                            service,
                            spreadsheet_id
                        ),
                        "dimension": "ROWS",
                        "startIndex": row_number - 1,
                        "endIndex": row_number
                    }
                }
            }
        ]
    }

    return service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=request
    ).execute()


def get_transactions_sheet_id(service, spreadsheet_id):

    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="sheets.properties"
    ).execute()

    for sheet in spreadsheet.get("sheets", []):

        properties = sheet["properties"]

        if properties["title"] == "Transactions":
            return properties["sheetId"]

    raise ValueError("Transactions worksheet not found.")
