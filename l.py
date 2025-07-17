#Solution simple : créer une liste de fichiers déjà traités
import pandas as pd
import os

weather_folder = "C:/plateforme-agricole-complete-v2/weather_cleaned"
variables = ["PRECTOTCORR", "IMERG_PRECTOT", "PS", "WS2M", "WS2M_MAX"]

# 🧠 Charger l'ancien fichier (si existant)
rows = []
try:
    df_existing = pd.read_csv("weather_afrique_restruc.csv")
    processed_files = set(df_existing['country'].unique())  # si chaque fichier correspond à un pays
    rows.extend(df_existing.to_dict('records'))
    print(f"✅ Fichiers déjà traités : {processed_files}")
except:
    processed_files = set()
    print("ℹ️ Aucun fichier météo existant trouvé — traitement complet")

# 🔁 Reprendre uniquement les fichiers non traités
for filename in os.listdir(weather_folder):
    if filename.endswith(".csv"):
        country_name = filename.replace("weather_", "").replace(".csv", "")
        if country_name in processed_files:
            print(f"⏭️ Ignoré : {filename} (déjà traité)")
            continue

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

# 💾 Export mis à jour
df_weather = pd.DataFrame(rows)
df_weather.to_csv("weather_afrique_restruc.csv", index=False)
print("✅ Export mis à jour : weather_afrique_restruc.csv")
