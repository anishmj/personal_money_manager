
import os

from dotenv import load_dotenv

from services.google_sheets import get_google_sheets_service
from services.settings_service import get_settings

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


def main():

    service = get_google_sheets_service()

    settings = get_settings(
        service,
        SPREADSHEET_ID
    )

    print("\nEXPENSE CATEGORIES")
    print(settings["expense_categories"])

    print("\nINCOME SOURCES")
    print(settings["income_sources"])

    print("\nPAYMENT METHODS")
    print(settings["payment_methods"])


if __name__ == "__main__":
    main()
