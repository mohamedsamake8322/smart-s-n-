import pandas as pd
import os

BASE_PATH = r"C:\plateforme-agricole-complete-v2\merged_outputs"
files = [f for f in os.listdir(BASE_PATH) if f.endswith(".csv.gz")]

def inspect_file(file_path, preview_rows=5):
    print(f"\n📂 Analyse de : {os.path.basename(file_path)}")
    try:
        df = pd.read_csv(file_path, dtype=str, low_memory=False, nrows=5000)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        print(f"🔢 Colonnes : {len(df.columns)} | 📄 Lignes chargées : {len(df)}\n")
        for col in df.columns:
            missing = df[col].isna().sum()
            unique_vals = df[col].dropna().unique()[:preview_rows]
            print(f"🔹 {col} | NaNs: {missing} | Exemples: {', '.join(unique_vals)}")
    except Exception as e:
        print(f"⛔ Erreur lecture : {e}")

print("📊 Inspection des structures en cours...")
for file in files:
    inspect_file(os.path.join(BASE_PATH, file))
