import constants as c
from googleapiclient.discovery import build
from helpers import get_google_credentials, fetch_drive_files, read_file


def main():
    """Main function to orchestrate the Google Drive file fetch process."""
    try:
        creds = get_google_credentials()
        service = build("drive", "v3", credentials=creds)
        files = fetch_drive_files(service, c.FOLDER_ID)
        for file in files:
            df = read_file(service, file['id'], file['name'])
    except Exception as e:
        print(f"An error occurred in main: {e}")
        return None


if __name__ == "__main__":
    main()
