import pandas as pd
import os

# Fichier à corriger
file_path = r"C:\plateforme-agricole-complete-v2\weather_cleaned\weather_Djibouti.csv"

try:
    # 🧪 Essai avec différents séparateurs
    df_try1 = pd.read_csv(file_path, sep=",", engine="python")
    df_try2 = pd.read_csv(file_path, sep=";", engine="python")

    # Sélectionne la version avec le plus grand nombre de colonnes utiles
    if df_try2.shape[1] > df_try1.shape[1]:
        df = df_try2
    else:
        df = df_try1

    # ✔️ Corriger Longitude si elle contient '.csv'
    if "Longitude" in df.columns:
        df["Longitude"] = df["Longitude"].astype(str).str.replace(".csv", "", regex=False)
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

    if "Latitude" in df.columns:
        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")

    # ✔️ Convertir les dates
    if "DATE" in df.columns:
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df["year"] = df["DATE"].dt.year

    # 🔍 Vérification finale
    if all(col in df.columns for col in ["DATE", "Latitude", "Longitude"]):
        df["latlon"] = df["Latitude"].round(4).astype(str) + "_" + df["Longitude"].round(4).astype(str)
        df.to_csv(file_path.replace("weather_cleaned", "weather_final"), index=False)
        print(f"✅ {os.path.basename(file_path)} corrigé et déplacé dans weather_final.")
    else:
        print(f"⚠️ Colonnes essentielles manquantes après tentative — à corriger manuellement.")
except Exception as e:
    print(f"⛔ Échec de lecture : {e}")
