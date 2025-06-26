import os
import mimetypes
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    creds = InstalledAppFlow.from_client_secrets_file(
        r"C:\Users\moham\Music\1\client_secret_363639044199-fase78nv9gfo3afuolkq9hhrnke96kdv.apps.googleusercontent.com.json",
        SCOPES
    ).run_local_server(port=0)
    return build('drive', 'v3', credentials=creds)

def create_folder_recursive(service, path_parts, parent_id=None, cache={}):
    current_path = ""
    for part in path_parts:
        current_path = os.path.join(current_path, part)
        if current_path in cache:
            parent_id = cache[current_path]
            continue
        folder_metadata = {
            'name': part,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        parent_id = folder['id']
        cache[current_path] = parent_id
    return parent_id

def upload_full_structure(service, local_root, drive_root_name):
    print(f"📁 Création du dossier Drive : {drive_root_name}")
    root_id = create_folder_recursive(service, [drive_root_name])

    for root, _, files in os.walk(local_root):
        rel_path = os.path.relpath(root, local_root)
        if rel_path == ".":
            drive_folder_id = root_id
        else:
            path_parts = [drive_root_name] + rel_path.split(os.sep)
            drive_folder_id = create_folder_recursive(service, path_parts)

        for file in files:
            file_path = os.path.join(root, file)
            mime_type, _ = mimetypes.guess_type(file_path)
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file_metadata = {
                'name': os.path.basename(file),
                'parents': [drive_folder_id]
            }
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"✅ Envoyé : {os.path.join(rel_path, file)}")

if __name__ == "__main__":
    dossier_local = r"C:\plateforme-agricole-complete-v2\plant_disease_dataset"
    nom_drive_root = "plant_disease_dataset"

    print("🔐 Authentification...")
    service = authenticate()
    print("📤 Upload avec structure complète...")
    upload_full_structure(service, dossier_local, nom_drive_root)
    print("✅ Upload terminé avec succès.")
