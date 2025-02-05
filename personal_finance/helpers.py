import io
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import constants as c


def get_google_credentials():
    """Handle Google Drive API authentication and return credentials."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", c.SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", c.SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def fetch_drive_files(service, folder_id):
    """Fetch files from specified Google Drive folder."""
    try:
        files = []
        page_token = None

        while True:
            response = (service.files().list(
                q=
                f"'{folder_id}' in parents and (mimeType='text/csv' or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
            ).execute())

            for file in response.get("files", []):
                print(f'Found file: {file.get("name")}, {file.get("id")}')

            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)

            if page_token is None:
                break

        return files

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def read_file(service, file_id, file_name):
    try:
        file_id = file_id

        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

        # Reset the file pointer to the beginning
        file.seek(0)

        if file_name.endswith('.xlsx'):
            df = pd.read_excel(file)
            print(f"File {file_name} loaded into DataFrame successfully")
            return df

        elif file_name.endswith('.csv'):
            df = pd.read_csv(file)
            print(f"File {file_name} loaded into DataFrame successfully")
            return df

        else:
            print(f"Unsupported file type: {file_name}")
            return None

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None
