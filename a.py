#🧪 Script Python : Cartographie des zones agro-optimales
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx  # pour fond de carte

# 📥 Charger le dataset fusionné
df = pd.read_csv("dataset_agronomique_final.csv")

# 🧼 Nettoyage basique
df = df.dropna(subset=["ph", "carbon_organic", "PRECTOTCORR", "longitude", "latitude"])

# 🎯 Définir les critères agro-optimaux
criteria = (
    (df["ph"] >= 5.8) & (df["ph"] <= 6.8) &  # pH légèrement acide / neutre
    (df["carbon_organic"] >= 1.5) &          # bonne matière organique
    (df["PRECTOTCORR"] >= 6) & (df["PRECTOTCORR"] <= 18)  # précipitations modérées
)

# 🧪 Extraire les lignes optimales
df_optimal = df[criteria]
print(f"✅ Points agro-optimaux détectés : {len(df_optimal)}")

# 🌍 Convertir en GeoDataFrame
gdf_optimal = gpd.GeoDataFrame(
    df_optimal,
    geometry=gpd.points_from_xy(df_optimal["longitude"], df_optimal["latitude"]),
    crs="EPSG:4326"
)

# 🔁 Reprojeter pour fond de carte
gdf_optimal = gdf_optimal.to_crs(epsg=3857)

# 🗺️ Affichage avec fond cartographique
fig, ax = plt.subplots(figsize=(12, 10))
gdf_optimal.plot(ax=ax, markersize=3, color="green", alpha=0.6)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
plt.title("🌿 Zones agro-optimales en Afrique (sol + pluie)")
plt.axis("off")
plt.tight_layout()
plt.show()

# 💾 Export GeoJSON si besoin
gdf_optimal.to_crs("EPSG:4326").to_file("zones_agro_optimales.geojson", driver="GeoJSON")
print("💾 Export GeoJSON terminé : zones_agro_optimales.geojson")
