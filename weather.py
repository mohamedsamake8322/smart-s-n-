import pandas as pd
import os
from glob import glob

# 📁 Dossiers
weather_folder = r"C:\plateforme-agricole-complete-v2\weather_cleaned"
output_folder = r"C:\plateforme-agricole-complete-v2\weather_final"
os.makedirs(output_folder, exist_ok=True)

report = []

# 🧽 Nettoyage par fichier
weather_files = glob(os.path.join(weather_folder, "*.csv"))
for file_path in weather_files:
    file_name = os.path.basename(file_path)

    if "report" in file_name.lower():
        continue  # Ignorer le fichier de rapport

    try:
        df = pd.read_csv(file_path, low_memory=False)

        # 🧠 Nettoyage Longitude
        if "Longitude" in df.columns:
            df["Longitude"] = df["Longitude"].astype(str).str.replace(".csv", "", regex=False)
            df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

        # ✔️ Vérification Latitude
        if "Latitude" in df.columns:
            df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")

        # 🧹 Suppression des colonnes avec >90% de NaN
        nan_threshold = 0.9
        df = df.dropna(axis=1, thresh=int((1 - nan_threshold) * len(df)))

        # ⛔ Limite colonne
        if df.shape[1] > 150 or df.shape[1] < 10:
            report.append({"file": file_name, "status": "Skipped (structure suspecte)", "rows": df.shape[0], "cols": df.shape[1]})
            continue

        # ✔️ Vérification colonnes essentielles
        essentials = {"DATE", "Latitude", "Longitude"}
        if not essentials.issubset(df.columns):
            report.append({"file": file_name, "status": "Skipped (colonnes essentielles manquantes)", "rows": df.shape[0], "cols": df.shape[1]})
            continue

        # ✅ Conversion de DATE
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")

        # 💾 Sauvegarde dans dossier final
        output_path = os.path.join(output_folder, file_name)
        df.to_csv(output_path, index=False)
        report.append({"file": file_name, "status": "✅ Corrigé et sauvegardé", "rows": df.shape[0], "cols": df.shape[1]})

    except Exception as e:
        report.append({"file": file_name, "status": f"Erreur de lecture : {e}", "rows": "-", "cols": "-"})

# 📊 Sauvegarde rapport
report_df = pd.DataFrame(report)
report_df.to_csv(os.path.join(output_folder, "weather_final_report.csv"), index=False)

print(f"🧼 Fichiers corrigés sauvegardés dans : {output_folder}")
print(f"📊 Rapport de nettoyage : weather_final_report.csv")
