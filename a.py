import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# 📥 Charger le fichier agronomique fusionné
df = pd.read_csv("dataset_agronomique_final.csv")

# 🔄 Pivot pour transformer variable ➝ colonne
df_pivot = df.pivot_table(
    index=["country", "date", "latitude", "longitude"],
    columns="variable",
    values="value"
).reset_index()

# 🧼 Supprimer les lignes sans infos clés
df_pivot = df_pivot.dropna(subset=["ph", "carbon_organic", "PRECTOTCORR", "latitude", "longitude"])

# 🎯 Définir les critères agro-optimaux
criteria = (
    (df_pivot["ph"] >= 5.8) & (df_pivot["ph"] <= 6.8) &
    (df_pivot["carbon_organic"] >= 1.5) &
    (df_pivot["PRECTOTCORR"] >= 6) & (df_pivot["PRECTOTCORR"] <= 18)
)

# 🧪 Extraire les points répondant aux critères
df_optimal = df_pivot[criteria]
print(f"✅ Points agro-optimaux détectés : {len(df_optimal)}")

# 🌍 Conversion en GeoDataFrame
gdf_optimal = gpd.GeoDataFrame(
    df_optimal,
    geometry=gpd.points_from_xy(df_optimal["longitude"], df_optimal["latitude"]),
    crs="EPSG:4326"
)

# 🔁 Reprojection pour fond de carte
gdf_optimal = gdf_optimal.to_crs(epsg=3857)

# 🗺️ Visualisation cartographique
fig, ax = plt.subplots(figsize=(12, 10))
gdf_optimal.plot(ax=ax, markersize=2, color="green", alpha=0.5)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
plt.title("🌿 Zones agro-optimales en Afrique (sol + pluie)")
plt.axis("off")
plt.tight_layout()
plt.show()

# 💾 Export des zones en GeoJSON
gdf_optimal.to_crs("EPSG:4326").to_file("zones_agro_optimales.geojson", driver="GeoJSON")
print("💾 Export terminé : zones_agro_optimales.geojson")
