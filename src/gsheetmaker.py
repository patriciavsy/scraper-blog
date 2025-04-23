from google.oauth2 import service_account 
from googleapiclient.discovery import build

from src.utils import sheets_name_generator

import os
from dotenv import load_dotenv
load_dotenv()



service_account_file = {
            "type": os.environ.get("TYPE"),
            "project_id": os.environ.get("GOOGLE_PROJECT_ID"),
            "private_key_id": os.environ.get("GOOGLE_PRIVATE_KEY_ID"),
            "private_key": os.environ.get("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.environ.get("GOOGLE_CLIENT_EMAIL"),
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
            "auth_uri": os.environ.get("GOOGLE_AUTH_URI"),
            "token_uri": os.environ.get("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.environ.get("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_X509_CERT_URL"),
            "universe_domain": os.environ.get("GOOGLE_UNIVERSE_DOMAIN")
}

scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]



credentials = service_account.Credentials.from_service_account_info(
    service_account_file, scopes=scopes
)

drive_service = build('drive', 'v3', credentials=credentials)
sheets_service = build('sheets', 'v4', credentials=credentials)





def create_sheet(category: str):
    spreadsheet = sheets_service.spreadsheets().create(
                        body={
                            'properties': {
                                'title': sheets_name_generator(category)
                            }
                        },
                        fields='spreadsheetId'
                    ).execute()

    sheet_id = spreadsheet['spreadsheetId']

    drive_service.files().update(
        fileId=sheet_id,
        addParents=os.environ.get("FOLDER_ID"),
        removeParents='root',
        fields='id, parents'
    ).execute()

    return sheet_id


def update_sheet(category: str, sheet_id: int, scraped_info):
    body = {
        'values': scraped_info
    }
    resultado = sheets_service.spreadsheets().values().append(
                    spreadsheetId=sheet_id,
                    range="Sheet1!A1",
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body=body
                ).execute()
    print(f"✅ {resultado.get('updates').get('updatedRows')} filas añadidas.")