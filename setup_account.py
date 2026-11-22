import os

from dotenv import load_dotenv
from services.google_sheets import get_google_sheets_service

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

ACCOUNT_HEADERS = ["Setting", "Value"]

ACCOUNT_DATA = [
    ["Initial Balance", 53491],
    ["Starting Date", "2026-11-01"],
    ["Currency", "INR"],
    ["November Migration Status", "Pending"]
]


def setup_account_sheet():

    service = get_google_sheets_service()

    spreadsheet = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets.properties"
    ).execute()

    existing = [
        s["properties"]["title"]
        for s in spreadsheet.get("sheets", [])
    ]

    if "Account" in existing:
        print("Account sheet already exists. No changes made.")
        return

    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "requests": [{
                "addSheet": {
                    "properties": {"title": "Account"}
                }
            }]
        }
    ).execute()

    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="'Account'!A1:B5",
        valueInputOption="USER_ENTERED",
        body={
            "values": [
                ACCOUNT_HEADERS,
                *ACCOUNT_DATA
            ]
        }
    ).execute()

    print("Account worksheet created successfully!")


if __name__ == "__main__":
    setup_account_sheet()