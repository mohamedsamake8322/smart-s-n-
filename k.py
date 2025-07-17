#🛠️ Mise à jour du Script 2 — Traitement de tous les fichiers météo
import pandas as pd
import os

# 📁 Dossier contenant les fichiers météo
weather_folder = "C:/plateforme-agricole-complete-v2/weather_cleaned"

# 🔎 Variables météo à extraire
variables = ["PRECTOTCORR", "IMERG_PRECTOT", "PS", "WS2M", "WS2M_MAX"]

# 📦 Stockage des lignes transformées
rows = []

# 🔁 Parcours de tous les fichiers CSV
for filename in os.listdir(weather_folder):
    if filename.endswith(".csv"):
        file_path = os.path.join(weather_folder, filename)
        print(f"📄 Traitement : {filename}")

        df_raw = pd.read_csv(file_path)
        for index, row in df_raw.iterrows():
            country = row.get("Country", "")
            date = pd.to_datetime(row.get("DATE", ""), errors="coerce")

            for col in df_raw.columns:
                for var in variables:
                    if col.startswith(var + "_"):
                        try:
                            lon = float(col.split("_")[1])
                            value = row[col]
                            rows.append({
                                "country": country,
                                "date": date,
                                "longitude": lon,
                                "variable": var,
                                "value": value
                            })
                        except:
                            continue

# 📊 Création du DataFrame final
df_weather = pd.DataFrame(rows)
print(f"✅ Météo restructurée : {df_weather.shape}")

# 💾 Export CSV
df_weather.to_csv("weather_afrique_restruc.csv", index=False)
print("📁 Export terminé : weather_afrique_restruc.csv")
