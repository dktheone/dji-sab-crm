import os
from django.core.management.base import BaseCommand
from django.conf import settings
from google_auth_oauthlib.flow import InstalledAppFlow

class Command(BaseCommand):
    help = 'Authenticates with Google Drive to generate token.json'

    def handle(self, *args, **kwargs):
        CREDENTIALS_FILE = settings.BASE_DIR / 'credentials.json'
        TOKEN_FILE = settings.BASE_DIR / 'token.json'
        SCOPES = ['https://www.googleapis.com/auth/drive.file']

        if not CREDENTIALS_FILE.exists():
            self.stdout.write(self.style.ERROR(f"File not found: {CREDENTIALS_FILE}"))
            self.stdout.write("Please download your OAuth 2.0 Client ID JSON from Google Cloud Console,")
            self.stdout.write("rename it to 'credentials.json', and place it in the project root.")
            return

        self.stdout.write("Starting authentication flow...")
        try:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            # Explicitly request offline access and force consent to get 'refresh_token'
            creds = flow.run_local_server(
                port=0, 
                access_type='offline', 
                prompt='consent'
            )
            
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            
            self.stdout.write(self.style.SUCCESS(f"Authentication successful! Token saved to {TOKEN_FILE}"))
            self.stdout.write("You can now run 'python manage.py backup_db'.")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Authentication failed: {e}"))
