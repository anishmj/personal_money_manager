
import os

from dotenv import load_dotenv

from services.google_sheets import get_google_sheets_service

from services.transaction_service import (
    create_transactions_sheet
)

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


def main():

    service = get_google_sheets_service()

    create_transactions_sheet(
        service,
        SPREADSHEET_ID
    )


if __name__ == "__main__":
    main()
