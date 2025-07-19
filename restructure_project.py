import os
import shutil

# Dossiers suggérés
structure = {
    "smart_agro_tools": ["ndvi_engine", "input_recommender", "db_interface", "utils", "dataset_loader.py", "api"],
    "dashboard": ["streamlit_dashboard", "pages", "templates", "assets"],
    "data": ["*.csv", "sample_datasets.py", "soil_sample_data.csv", "weather_sample_data.csv"],
    "models": ["train_yield_predictor.py", "model_optimizer.py", "ml_models.py", "advanced_ai_models.py"],
    "legacy_modules": ["deafrica-tools", "Beginners_guide", "deafrica-sandbox-notebooks"],
    "services": ["iot_system.py", "blockchain_system.py", "voice_assistant.py", "pdf_generator.py"]
}

# Scan et suggestion
def scan_project(base_path):
    manifest = []
    for root, dirs, files in os.walk(base_path):
        depth = root.replace(base_path, "").count(os.sep)
        indent = "│   " * depth
        manifest.append(f"{indent}├── {os.path.basename(root)}/")
        for f in files:
            manifest.append(f"{indent}│   └── {f}")
    return manifest

# Génération Markdown
def save_manifest(manifest, output="project_manifest.md"):
    with open(output, "w") as f:
        f.write("# 🗂️ Arborescence du projet SènèSmart\n\n")
        f.write("\n".join(manifest))
    print(f"✅ Manifest sauvegardé dans {output}")

# Lancement
if __name__ == "__main__":
    base = r"C:\plateforme-agricole-complete-v2"
    tree = scan_project(base)
    save_manifest(tree)
