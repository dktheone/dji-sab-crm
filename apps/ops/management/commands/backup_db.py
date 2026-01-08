import os
import datetime
import py7zr
import requests
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class Command(BaseCommand):
    help = 'Backs up the SQLite database to a 7z file, uploads to cloud, and manages retention.'

    def handle(self, *args, **kwargs):
        # Configuration
        DB_FILE = settings.BASE_DIR / 'db.sqlite3'
        BACKUP_DIR = settings.BASE_DIR / 'backups'
        BACKUP_DIR.mkdir(exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'db_backup_{timestamp}.7z'
        backup_path = BACKUP_DIR / backup_filename

        # 1. Local Backup (7z Compression)
        self.stdout.write(f"Creating local backup: {backup_path}")
        try:
            with py7zr.SevenZipFile(backup_path, 'w') as archive:
                archive.write(DB_FILE, arcname='db.sqlite3')
            self.stdout.write(self.style.SUCCESS(f"Successfully created {backup_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create backup: {e}"))
            return

        # 2. Telegram Backup
        tele_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        tele_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if tele_token and tele_chat_id:
            self.stdout.write("Uploading to Telegram...")
            try:
                url = f"https://api.telegram.org/bot{tele_token}/sendDocument"
                with open(backup_path, 'rb') as f:
                    files = {'document': f}
                    data = {'chat_id': tele_chat_id, 'caption': f"DB Backup: {backup_filename}"}
                    response = requests.post(url, files=files, data=data)
                    if response.status_code == 200:
                        self.stdout.write(self.style.SUCCESS("Successfully uploaded to Telegram"))
                    else:
                        self.stdout.write(self.style.ERROR(f"Telegram upload failed: {response.text}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Telegram upload error: {e}"))
        else:
            self.stdout.write("Skipping Telegram upload (credentials missing)")

        # 3. Google Drive Backup
        gdrive_folder_id = os.environ.get('GDRIVE_FOLDER_ID')
        token_file = settings.BASE_DIR / 'token.json'
        print("token_file", token_file, token_file.exists())
        
        if gdrive_folder_id and token_file.exists():
            self.stdout.write("Uploading to Google Drive...")
            try:
                from google.oauth2.credentials import Credentials
                from google.auth.transport.requests import Request

                creds = Credentials.from_authorized_user_file(str(token_file), ['https://www.googleapis.com/auth/drive.file'])
                
                # Check for expiry and refresh
                if creds.expired and creds.refresh_token:
                    self.stdout.write("Token expired, refreshing...")
                    creds.refresh(Request())
                    # Save refreshed token
                    with open(token_file, 'w') as token:
                        token.write(creds.to_json())

                service = build('drive', 'v3', credentials=creds)
                
                file_metadata = {
                    'name': backup_filename,
                    'parents': [gdrive_folder_id]
                }
                media = MediaFileUpload(backup_path, mimetype='application/x-7z-compressed')
                
                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                self.stdout.write(self.style.SUCCESS(f"Successfully uploaded to Google Drive (File ID: {file.get('id')})"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Google Drive upload error: {e}"))
        else:
            self.stdout.write("Skipping Google Drive upload (credentials missing or token.json not found)")

        # 4. Retention Policy (Delete older than 7 days)
        self.stdout.write("Checking retention policy...")
        retention_days = 7
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=retention_days)
        
        for file in BACKUP_DIR.glob('db_backup_*.7z'):
            try:
                file_mtime = datetime.datetime.fromtimestamp(file.stat().st_mtime)
                if file_mtime < cutoff_time:
                    file.unlink()
                    self.stdout.write(self.style.WARNING(f"Deleted old backup: {file.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error deleting file {file.name}: {e}"))

        self.stdout.write(self.style.SUCCESS("Backup process completed."))
