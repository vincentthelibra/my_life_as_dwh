import io
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_google_credentials():
    """Handle Google Drive API authentication and return credentials."""
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def fetch_drive_files(service, folder_id='1c7jJbH1v5lyEIS1tG2yBkfIZx9cEx43f'):
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


def download_file(service, file_id, file_name):
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


def main():
    """Main function to orchestrate the Google Drive file fetch process."""
    try:
        creds = get_google_credentials()
        service = build("drive", "v3", credentials=creds)
        files = fetch_drive_files(service)
        for file in files:
            download_file(service, file['id'], file['name'])
    except Exception as e:
        print(f"An error occurred in main: {e}")
        return None


if __name__ == "__main__":
    main()
