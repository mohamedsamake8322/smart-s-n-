import pandas as pd
import os
from glob import glob

# Dossier source et cible
source_folder = r"C:\plateforme-agricole-complete-v2\weather_by_country"
cleaned_folder = r"C:\plateforme-agricole-complete-v2\weather_cleaned"
os.makedirs(cleaned_folder, exist_ok=True)

# Rapport
report = []

# Scan et correction
weather_files = glob(os.path.join(source_folder, "*.csv"))

for file_path in weather_files:
    file_name = os.path.basename(file_path)
    try:
        df = pd.read_csv(file_path, low_memory=False)

        # Vérification des colonnes de base
        essential_cols = {"DATE", "Latitude", "Longitude"}
        has_essentials = essential_cols.issubset(df.columns)

        # Correction de longitude si elle contient '.csv'
        if "Longitude" in df.columns:
            df["Longitude"] = df["Longitude"].astype(str).str.replace(".csv", "", regex=False)
            df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

        # Normalisation latitude
        if "Latitude" in df.columns:
            df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")

        # Vérification du nombre de colonnes raisonnable
        if df.shape[1] > 150:
            report.append({"file": file_name, "status": "Too many columns — Ignored", "rows": df.shape[0], "cols": df.shape[1]})
            continue
        elif not has_essentials:
            report.append({"file": file_name, "status": "Missing essential columns — Ignored", "rows": df.shape[0], "cols": df.shape[1]})
            continue

        # Conversion de date
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")

        # Sauvegarde nettoyée
        output_path = os.path.join(cleaned_folder, file_name)
        df.to_csv(output_path, index=False)
        report.append({"file": file_name, "status": "Cleaned and saved", "rows": df.shape[0], "cols": df.shape[1]})

    except Exception as e:
        report.append({"file": file_name, "status": f"Read error: {e}", "rows": "-", "cols": "-"})


# Génération du rapport
report_df = pd.DataFrame(report)
report_path = os.path.join(cleaned_folder, "weather_cleaning_report.csv")
report_df.to_csv(report_path, index=False)
print(f"✅ Rapport de nettoyage généré ici : {report_path}")
print(f"🧼 Fichiers météo nettoyés et sauvegardés dans : {cleaned_folder}")
