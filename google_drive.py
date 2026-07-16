import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveManager:
    def __init__(self, credentials_path="credentials.json", token_path="token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.creds = None

    def authenticate(self):
        """Authenticates and creates the Google Drive service object."""
        self.creds = None
        
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file '{self.credentials_path}' not found. Please provide it in the Settings.")
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('drive', 'v3', credentials=self.creds)
        return True

    def _get_or_create_folder(self, folder_name, parent_id=None):
        """Finds a folder by name or creates it if it doesn't exist."""
        if not self.service:
            self.authenticate()

        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)').execute()
        items = results.get('files', [])

        if not items:
            # Create the folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            return folder.get('id')
        else:
            return items[0].get('id')

    def upload_file(self, filepath, customer_code):
        """Uploads a file to a specific customer's folder inside CRM_Documents."""
        if not self.service:
            self.authenticate()

        # 1. Get or create root folder 'CRM_Documents'
        root_folder_id = self._get_or_create_folder('CRM_Documents')

        # 2. Get or create customer folder
        customer_folder_id = self._get_or_create_folder(customer_code, parent_id=root_folder_id)

        # 3. Upload file
        filename = os.path.basename(filepath)
        file_metadata = {
            'name': filename,
            'parents': [customer_folder_id]
        }
        media = MediaFileUpload(filepath, resumable=True)
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        return file.get('id'), file.get('webViewLink')

# Global instance for easier reuse across the app
gdrive_mgr = GoogleDriveManager()
