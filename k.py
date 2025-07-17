import pandas as pd
import os

# 📁 Dossier contenant les fichiers météo
weather_folder = "C:/plateforme-agricole-complete-v2/weather_cleaned"

# 📦 Stockage des lignes transformées
rows = []

# 🔁 Parcours de tous les fichiers CSV météo
for filename in os.listdir(weather_folder):
    if filename.endswith(".csv"):
        file_path = os.path.join(weather_folder, filename)
        print(f"📄 Traitement : {filename}")

        df_raw = pd.read_csv(file_path)

        for index, row in df_raw.iterrows():
            country = row.get("Country", "")
            date = pd.to_datetime(row.get("DATE", ""), errors="coerce")
            latitude = row.get("Latitude", None)

            for col in df_raw.columns:
                # Skip known metadata columns
                if col in ["Country", "Latitude", "Longitude", "DATE"]:
                    continue

                try:
                    # Déduction de la variable et de la longitude
                    if "_" in col:
                        var, lon_str = col.rsplit("_", 1)
                        lon = float(lon_str)
                    else:
                        var = col
                        lon = row.get("Longitude", None)

                    value = row[col]

                    rows.append({
                        "country": country,
                        "date": date,
                        "latitude": latitude,
                        "longitude": lon,
                        "variable": var,
                        "value": value
                    })
                except:
                    continue

# 📊 Créer le DataFrame final
df_weather = pd.DataFrame(rows)
print(f"✅ Météo restructurée : {df_weather.shape}")

# 💾 Export CSV final
output_path = "C:/plateforme-agricole-complete-v2/Boua/weather_afrique_restruc_total.csv"
df_weather.to_csv(output_path, index=False)
print(f"📁 Export terminé : {output_path}")
