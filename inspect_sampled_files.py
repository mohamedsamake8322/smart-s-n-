import pandas as pd
import os

BASE_PATH = r"C:\plateforme-agricole-complete-v2\merged_outputs"
files = [f for f in os.listdir(BASE_PATH) if f.endswith(".csv.gz")]

def inspect_preview(file_path, preview_rows=5):
    print(f"\n📂 Fichier : {os.path.basename(file_path)}")
    try:
        df = pd.read_csv(file_path, dtype=str, nrows=preview_rows)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        print(f"🔢 Colonnes ({len(df.columns)}): {df.columns.tolist()}")
        print(f"\n👀 Aperçu des {preview_rows} lignes :")
        print(df.head(preview_rows).to_string(index=False))
    except Exception as e:
        print(f"⛔ Erreur lecture : {e}")

print("📊 Inspection rapide des fichiers...")
for file in files:
    inspect_preview(os.path.join(BASE_PATH, file))
