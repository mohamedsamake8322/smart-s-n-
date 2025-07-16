import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def attribuer_pays_aux_points(
    fichier_points,
    shapefile_pays,
    output_path="soil_profile_africa_with_country.csv",
    source_crs="EPSG:3857"  # 🔁 À ajuster si tu connais la vraie projection
):
    # 📥 Lecture initiale du fichier
    df = pd.read_csv(fichier_points)
    print("🔎 Colonnes disponibles :", df.columns.tolist())

    # 🔍 Tentative automatique d'identification des coordonnées
    colonnes = df.columns.tolist()
    x_col = colonnes[0] if len(colonnes) > 1 else None
    y_col = colonnes[1] if len(colonnes) > 1 else None

    if x_col is None or y_col is None:
        raise ValueError("❌ Impossible d'identifier les colonnes X/Y.")

    print(f"🧭 Tentative d'utilisation de '{x_col}' comme X et '{y_col}' comme Y")
    df.rename(columns={x_col: 'X', y_col: 'Y'}, inplace=True)

    # 🧼 Nettoyage des coordonnées
    df['X'] = pd.to_numeric(df['X'], errors='coerce')
    df['Y'] = pd.to_numeric(df['Y'], errors='coerce')
    df = df.dropna(subset=['X', 'Y'])

    # 🌐 Création des géométries
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df['X'], df['Y'])],
        crs=source_crs
    )
    gdf_points = gdf_points.to_crs("EPSG:4326")

    # 🗺️ Chargement du shapefile des pays
    gdf_pays = gpd.read_file(shapefile_pays).to_crs("EPSG:4326")

    # 🔗 Spatial join
    gdf_joined = gpd.sjoin(
        gdf_points,
        gdf_pays[['ADMIN', 'geometry']],
        how="left",
        predicate="intersects"
    )
    gdf_joined.rename(columns={"ADMIN": "Country"}, inplace=True)

    # 📤 Export final
    gdf_joined.drop(columns=['geometry', 'index_right'], errors='ignore').to_csv(output_path, index=False)

    # ✅ Résumé
    print(f"✅ Fichier enrichi enregistré : {output_path}")
    print(f"🌍 Pays détectés : {gdf_joined['Country'].nunique()}")
    print(gdf_joined['Country'].value_counts().head())

# 🔧 Exemple d’usage
attribuer_pays_aux_points(
    fichier_points = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv",
    shapefile_pays = r"C:\Users\moham\Documents\naturalearth_lowres\ne_110m_admin_0_countries.shp",
    output_path = r"C:\plateforme-agricole-complete-v2\soil_profile_africa_with_country.csv",
    source_crs = "EPSG:3857"  # ↩︎ Modifie si tu connais l'origine exacte de la projection
)
