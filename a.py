import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# 📥 Charger le fichier agronomique fusionné
df = pd.read_csv("dataset_agronomique_final.csv")

# 🔄 Pivot : transformer variable en colonnes météo
df_meteo = df.pivot_table(
    index=["country", "date", "latitude_x", "longitude_x"],
    columns="variable",
    values="value"
).reset_index()

# 🧪 Fusion météo + sol (on récupère les colonnes du sol une seule fois)
cols_sol = ["ph", "carbon_organic"]
df_sol = df.drop_duplicates(subset=["latitude_y", "longitude_y"])[["latitude_y", "longitude_y"] + cols_sol]

# 📦 Fusion des deux ensembles par coordonnées
df_full = pd.merge(
    df_meteo,
    df_sol,
    left_on=["latitude_x", "longitude_x"],
    right_on=["latitude_y", "longitude_y"],
    how="left"
)

# 🧼 Supprimer les lignes incomplètes
df_clean = df_full.dropna(subset=["ph", "carbon_organic", "PRECTOTCORR", "latitude_x", "longitude_x"])

# 🎯 Définir les critères agro-optimaux
criteria = (
    (df_clean["ph"] >= 5.8) & (df_clean["ph"] <= 6.8) &
    (df_clean["carbon_organic"] >= 1.5) &
    (df_clean["PRECTOTCORR"] >= 6) & (df_clean["PRECTOTCORR"] <= 18)
)

df_optimal = df_clean[criteria]
print(f"✅ Points agro-optimaux détectés : {len(df_optimal)}")

# 🌍 Conversion en GeoDataFrame
gdf_optimal = gpd.GeoDataFrame(
    df_optimal,
    geometry=gpd.points_from_xy(df_optimal["longitude_x"], df_optimal["latitude_x"]),
    crs="EPSG:4326"
)

# 🔁 Reprojection pour fond carto
gdf_optimal = gdf_optimal.to_crs(epsg=3857)

# 🗺️ Affichage
fig, ax = plt.subplots(figsize=(12, 10))
gdf_optimal.plot(ax=ax, markersize=2, color="green", alpha=0.5)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
plt.title("🌿 Zones agro-optimales en Afrique (sol + pluie)")
plt.axis("off")
plt.tight_layout()
plt.show()

# 💾 Export GeoJSON
gdf_optimal.to_crs("EPSG:4326").to_file("zones_agro_optimales.geojson", driver="GeoJSON")
print("💾 Export terminé : zones_agro_optimales.geojson")
