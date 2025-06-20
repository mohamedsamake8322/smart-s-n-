from huggingface_hub import create_repo, upload_file

REPO_ID = "mohamedsamake8322/smartagro-efficientnet-resnet"

# S'assure que le repo existe (sinon le crée)
create_repo(repo_id=REPO_ID, repo_type="model", exist_ok=True)

# Upload du fichier labels.json
upload_file(
    path_or_fileobj="model/labels.json",
    path_in_repo="labels.json",
    repo_id=REPO_ID,
    repo_type="model"
)

print("✅ labels.json uploadé sur Hugging Face avec succès.")
