
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]

BASE_DIR = Path(__file__).resolve().parent

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def authenticate():

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        SCOPES
    )

    credentials = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(credentials.to_json())

    print("Google authentication successful!")
    print("Token saved successfully.")


if __name__ == "__main__":
    authenticate()
