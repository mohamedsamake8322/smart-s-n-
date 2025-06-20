from huggingface_hub import upload_file

upload_file(
    path_or_fileobj="model/efficientnet_resnet.keras",
    path_in_repo="efficientnet_resnet.keras",
    repo_id="mohamedsamake8322/smartagro-efficientnet-resnet",
    repo_type="model"
)

print("✅ Modèle `.keras` uploadé avec succès sur Hugging Face 🚀")
