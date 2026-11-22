
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only access for our first connection test
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

SPREADSHEET_ID = "12Z6V5A4VGyJdPTzXyXdrDq1VVvKmdaNUAK64XwvYxcw"


def authenticate_google():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json", SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def connect_to_google_sheets():

    credentials = authenticate_google()

    service = build(
        "sheets",
        "v4",
        credentials=credentials
    )

    return service


def get_sheet_names(service):

    spreadsheet = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID
    ).execute()

    print("\nConnected successfully!")

    print("Spreadsheet:", spreadsheet["properties"]["title"])

    print("\nAvailable sheets:")

    for sheet in spreadsheet["sheets"]:

        title = sheet["properties"]["title"]

        print("-", title)


def main():

    service = connect_to_google_sheets()

    get_sheet_names(service)


if __name__ == "__main__":
    main()
