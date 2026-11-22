
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent.parent

TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


def get_google_sheets_service():

    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            "token.json not found. Run python auth.py first."
        )

    credentials = Credentials.from_authorized_user_file(
        str(TOKEN_FILE),
        SCOPES
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

        TOKEN_FILE.write_text(credentials.to_json())

    if not credentials.valid:
        raise RuntimeError(
            "Google credentials are invalid. Run python auth.py again."
        )

    service = build(
        "sheets",
        "v4",
        credentials=credentials
    )

    return service


def get_spreadsheet_details(service, spreadsheet_id):

    spreadsheet = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        fields="properties.title,sheets.properties"
    ).execute()

    return spreadsheet
