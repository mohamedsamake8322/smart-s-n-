import os
from glob import glob

# Dossier racine du projet
ROOT = r"C:\plateforme-agricole-complete-v2"

# Structure cible (modulaire et recommandée)
RECOMMENDED_STRUCTURE = {
    "smart_agro_tools": ["ndvi_engine", "input_recommender", "db_interface", "utils", "dataset_loader.py", "api"],
    "dashboard": ["pages", "components", "templates", "streamlit_dashboard"],
    "data": ["*.csv", "sample_datasets.py"],
    "models": ["train_yield_predictor.py", "model_optimizer.py", "ml_models.py"],
    "services": ["iot_system.py", "blockchain_system.py", "voice_assistant.py", "pdf_generator.py"],
    "legacy_modules": ["deafrica-tools", "Beginners_guide", "deafrica-sandbox-notebooks", "Scripts"],
    "assets": ["fonts", "attached_assets", "banner_agriculture.jpg"],
    "config": [".env", "*.yaml", "parameters.json"]
}

def find_matches(name):
    """Trouve les fichiers/dossiers correspondant dans ROOT"""
    matches = []
    if "*" in name:
        matches = glob(os.path.join(ROOT, name), recursive=True)
    else:
        candidate = os.path.join(ROOT, name)
        if os.path.exists(candidate):
            matches = [candidate]
    return matches

def simulate_organization():
    print("🧠 Simulation de réorganisation — aucune action réelle\n")
    for target_folder, items in RECOMMENDED_STRUCTURE.items():
        print(f"📁 {target_folder}/")
        for item in items:
            found = find_matches(item)
            for f in found:
                print(f"  🔸 {os.path.relpath(f, ROOT)} → {target_folder}/")
        print("")

if __name__ == "__main__":
    simulate_organization()
