import pandas as pd

# 🔗 Chemins vers tes fichiers
soil_path = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv"
weather_path = r"C:\plateforme-agricole-complete-v2\weather_reduit\weather_Mali.csv"  # ← choisis un fichier réduit

# 🌱 Chargement du sol
soil_df = pd.read_csv(soil_path)
soil_df["Latitude"] = soil_df["y"]
soil_df["Longitude"] = soil_df["x"]
soil_df["latlon"] = soil_df["Latitude"].round(4).astype(str) + "_" + soil_df["Longitude"].round(4).astype(str)
soil_latlon = set(soil_df["latlon"].dropna().unique())

print(f"🌱 Points sol : {len(soil_latlon)}")
print("🔎 Exemples latlon sol :", list(soil_latlon)[:5])

# 🌦️ Chargement météo (réduit)
weather_df = pd.read_csv(weather_path, low_memory=False)
weather_df["Latitude"] = pd.to_numeric(weather_df["Latitude"], errors="coerce")
weather_df["Longitude"] = pd.to_numeric(weather_df["Longitude"].astype(str).str.replace(".csv", "", regex=False), errors="coerce")
weather_df["latlon"] = weather_df["Latitude"].round(4).astype(str) + "_" + weather_df["Longitude"].round(4).astype(str)
weather_latlon = set(weather_df["latlon"].dropna().unique())

print(f"🌦️ Points météo : {len(weather_latlon)}")
print("🔎 Exemples latlon météo :", list(weather_latlon)[:5])

# 🧩 Intersections
common_latlon = soil_latlon & weather_latlon
print(f"🔗 Points communs latlon : {len(common_latlon)}")

# 🗺️ Vérification de la clé Country/Year
print("🌍 Exemples pays météo :", weather_df["Country"].dropna().unique()[:5])
weather_df["DATE"] = pd.to_datetime(weather_df["DATE"], errors="coerce")
weather_df["year"] = weather_df["DATE"].dt.year
print("📆 Exemples années météo :", sorted(weather_df["year"].dropna().unique())[:5])
