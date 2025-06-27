import shutil
import os

source = r"C:\plateforme-agricole-complete-v2\plantdataset"
destination = r"H:\My Drive\plantdataset"

print("🔍 Vérification de l'existence du dossier source...")
if not os.path.exists(source):
    raise FileNotFoundError(f"❌ Le dossier source n'existe pas : {source}")

print("📁 Création du dossier de destination s'il n'existe pas déjà...")
os.makedirs(os.path.dirname(destination), exist_ok=True)

print(f"🚀 Déplacement du dossier de:\n   {source}\nvers:\n   {destination}")
shutil.move(source, destination)

print("✅ Dossier déplacé avec succès.")
