import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# 📥 Charger ton fichier fusionné
df = pd.read_csv("dataset_agronomique_final.csv")

# 🔄 Transformer le format vertical météo → horizontal
df_meteo = df.pivot_table(
    index=["country", "date", "latitude_x", "longitude_x"],
    columns="variable",
    values="value"
).reset_index()

# 📌 Colonnes pédologiques clés
cols_sol = ["ph", "carbon_organic"]
df_sol = df.drop_duplicates(subset=["latitude_y", "longitude_y"])[["latitude_y", "longitude_y"] + cols_sol]

# 🔗 Fusion météo + sol
df_full = pd.merge(
    df_meteo,
    df_sol,
    left_on=["latitude_x", "longitude_x"],
    right_on=["latitude_y", "longitude_y"],
    how="left"
)

# ✅ Colonnes nécessaires (vérification)
required_columns = ["ph", "carbon_organic", "PRECTOTCORR", "latitude_x", "longitude_x"]
existing_columns = [col for col in required_columns if col in df_full.columns]

df_clean = df_full.dropna(subset=existing_columns)

# 📊 Afficher les stats par critère
print("\n📊 Statistiques des variables clés :")
for col in ["ph", "carbon_organic", "PRECTOTCORR"]:
    if col in df_clean.columns:
        print(f"\n--- {col} ---")
        print(df_clean[col].describe())

# ✅ Points valides par critère
print("\n✅ Points valides par critère :")
if "ph" in df_clean.columns:
    print("PH entre 5.5–7.5 :", df_clean[(df_clean["ph"] >= 5.5) & (df_clean["ph"] <= 7.5)].shape[0])
if "carbon_organic" in df_clean.columns:
    print("Carbone ≥ 1.0 :", df_clean[df_clean["carbon_organic"] >= 1.0].shape[0])
if "PRECTOTCORR" in df_clean.columns:
    print("Précipitations entre 5–20 :", df_clean[(df_clean["PRECTOTCORR"] >= 5) & (df_clean["PRECTOTCORR"] <= 20)].shape[0])

# 🧪 Définir critères souples
criteria = (
    (df_clean["ph"] >= 5.5) & (df_clean["ph"] <= 7.5) &
    (df_clean["carbon_organic"] >= 1.0)
)

if "PRECTOTCORR" in df_clean.columns:
    criteria &= (df_clean["PRECTOTCORR"] >= 5) & (df_clean["PRECTOTCORR"] <= 20)

df_optimal = df_clean[criteria]
print(f"\n✅ Nombre final de points agro-optimaux : {len(df_optimal)}")

# 🌍 GeoDataFrame
gdf_optimal = gpd.GeoDataFrame(
    df_optimal,
    geometry=gpd.points_from_xy(df_optimal["longitude_x"], df_optimal["latitude_x"]),
    crs="EPSG:4326"
).to_crs(epsg=3857)

# 🗺️ Visualisation
if not gdf_optimal.empty:
    fig, ax = plt.subplots(figsize=(12, 10))
    gdf_optimal.plot(ax=ax, markersize=2, color="green", alpha=0.5)
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
    plt.title("🌿 Zones agro-optimales (sol + pluie)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

    # 💾 Export GeoJSON
    gdf_optimal.to_crs("EPSG:4326").to_file("zones_agro_optimales.geojson", driver="GeoJSON")
    print("\n💾 Export terminé : zones_agro_optimales.geojson")
else:
    print("\n⚠️ Aucun point ne répond aux critères assouplis. Essaye avec des plages encore plus larges ou explore pays par pays.")
