import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def attribuer_pays_aux_points(
    fichier_points,
    shapefile_pays,
    output_path="soil_profile_africa_with_country.csv",
    source_crs="EPSG:3857"  # ← À adapter si nécessaire
):
    # 📥 Charger les données et renommer les colonnes de coordonnées
    df = pd.read_csv(fichier_points)
    df.rename(columns={'00cm': 'X', 'soc_100-200cm': 'Y'}, inplace=True)

    # 🧼 Nettoyer les coordonnées
    df['X'] = pd.to_numeric(df['X'], errors='coerce')
    df['Y'] = pd.to_numeric(df['Y'], errors='coerce')
    df = df.dropna(subset=['X', 'Y'])

    # 🌐 Créer les géométries en projection native
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df['X'], df['Y'])],
        crs=source_crs
    )

    # 🔄 Reprojeter en WGS84 pour le croisement avec les pays
    gdf_points = gdf_points.to_crs("EPSG:4326")

    # 🗺️ Charger le shapefile des pays et l’harmoniser
    gdf_pays = gpd.read_file(shapefile_pays)
    gdf_pays = gdf_pays.to_crs("EPSG:4326")

    # 🔗 Spatial join
    gdf_joined = gpd.sjoin(
        gdf_points,
        gdf_pays[['ADMIN', 'geometry']],
        how="left",
        predicate="intersects"
    )
    gdf_joined.rename(columns={"ADMIN": "Country"}, inplace=True)

    # 📤 Exporter le résultat final
    gdf_joined.drop(columns=['geometry', 'index_right'], errors='ignore').to_csv(output_path, index=False)

    # ✅ Résumé de l’enrichissement
    print(f"✅ Fichier enrichi enregistré : {output_path}")
    print(f"🌍 Pays détectés : {gdf_joined['Country'].nunique()}")
    print(gdf_joined['Country'].value_counts().head())

# 🔧 Exemple d’usage
attribuer_pays_aux_points(
    fichier_points = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv",
    shapefile_pays = r"C:\Users\moham\Documents\naturalearth_lowres\ne_110m_admin_0_countries.shp",
    output_path = r"C:\plateforme-agricole-complete-v2\soil_profile_africa_with_country.csv",
    source_crs = "EPSG:3857"  # ← ou autre selon l'origine des coordonnées X/Y
)
