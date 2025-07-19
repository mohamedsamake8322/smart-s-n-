import os
import shutil
import argparse
from glob import glob

ROOT = r"C:\plateforme-agricole-complete-v2"
REPORT = os.path.join(ROOT, "restructuring_report.txt")

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

def safe_move(src_path, dst_folder):
    os.makedirs(dst_folder, exist_ok=True)
    basename = os.path.basename(src_path)
    dst_path = os.path.join(dst_folder, basename)
    try:
        shutil.move(src_path, dst_path)
        return f"✅ {basename} → {dst_folder}"
    except Exception as e:
        return f"❌ Échec déplacement de {basename} → {dst_folder} ({e})"

def run_organization(apply=False):
    log = []
    log.append(f"Mode : {'APPLY' if apply else 'DRY-RUN'}\n")
    for target_folder, items in RECOMMENDED_STRUCTURE.items():
        target_path = os.path.join(ROOT, target_folder)
        os.makedirs(target_path, exist_ok=True)
        log.append(f"\n📁 {target_folder}/")
        for item in items:
            if "*" in item:
                found = glob(os.path.join(ROOT, item))
            else:
                candidate = os.path.join(ROOT, item)
                found = [candidate] if os.path.exists(candidate) else []
            for f in found:
                rel = os.path.relpath(f, ROOT)
                if apply:
                    result = safe_move(f, target_path)
                else:
                    result = f"🔹 {rel} → {target_folder}/"
                log.append(result)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    print(f"📄 Rapport sauvegardé dans : {REPORT}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Exécuter la réorganisation réelle")
    args = parser.parse_args()
    run_organization(apply=args.apply)
