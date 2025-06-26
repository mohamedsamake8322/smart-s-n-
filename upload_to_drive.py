import os
import mimetypes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🔐 Portée Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    creds = InstalledAppFlow.from_client_secrets_file(
    r"C:\Users\moham\Music\1\client_secret_363639044199-fase78nv9gfo3afuolkq9hhrnke96kdv.apps.googleusercontent.com.json",
    SCOPES
).run_local_server(port=0)

    return build('drive', 'v3', credentials=creds)

def create_drive_folder(service, folder_name, parent_id=None):
    metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        metadata['parents'] = [parent_id]
    folder = service.files().create(body=metadata, fields='id').execute()
    return folder['id']

def upload_file(service, file_path, parent_id):
    name = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    metadata = {'name': name, 'parents': [parent_id]}
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    service.files().create(body=metadata, media_body=media, fields='id').execute()
    print(f"✅ Fichier envoyé : {name}")

def upload_folder(service, folder_path, parent_id=None):
    for root, _, files in os.walk(folder_path):
        rel_path = os.path.relpath(root, folder_path)
        current_parent = parent_id
        if rel_path != ".":
            current_parent = create_drive_folder(service, rel_path, parent_id)
        for file in files:
            upload_file(service, os.path.join(root, file), current_parent)

# 🚀 Lancement
if __name__ == "__main__":
    dossier_local = r"C:\plateforme-agricole-complete-v2\plant_disease_dataset"
    print("🔐 Authentification...")
    service = authenticate()
    print("📁 Création du dossier 'plantdataset' sur Drive...")
    dossier_drive_id = create_drive_folder(service, "plantdataset")
    print("📤 Début de l'upload...")
    upload_folder(service, dossier_local, dossier_drive_id)
    print("✅ Upload terminé avec succès.")
