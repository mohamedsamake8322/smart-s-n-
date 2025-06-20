from huggingface_hub import create_repo, upload_file

# Étape 1 : Créer le dépôt si besoin
create_repo(
    repo_id="mohamedsamake8322/smartagro-efficientnet-resnet",
    repo_type="model",
    exist_ok=True  # Ne plante pas si le repo existe déjà
)

# Étape 2 : Uploader ton fichier .keras
upload_file(
    path_or_fileobj="model/efficientnet_resnet.keras",
    path_in_repo="efficientnet_resnet.keras",
    repo_id="mohamedsamake8322/smartagro-efficientnet-resnet",
    repo_type="model"
)

print("✅ Modèle `.keras` uploadé avec succès sur Hugging Face 🚀")
