import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 📥 Chargement du fichier CSV
df_sol = pd.read_csv("soil_profile_africa_reprojected.csv")

# 🌍 Création de la géométrie à partir des coordonnées
geometry = [Point(xy) for xy in zip(df_sol['Longitude'], df_sol['Latitude'])]
gdf_sol = gpd.GeoDataFrame(df_sol, geometry=geometry, crs="EPSG:4326")

try:
    # 📦 Chargement du shapefile (vérifier que le fichier existe à ce chemin)
    shapefile_path = r"C:\Users\moham\Documents\naturalearth_lowres\ne_110m_admin_0_countries.shp"
    africa = gpd.read_file(shapefile_path)

    # 🧠 Affiche les colonnes disponibles pour vérification
    print("🔍 Colonnes dans le shapefile :", africa.columns.tolist())

    # 🌍 Filtrage des pays africains (si 'continent' n'existe pas, alternative par noms)
    if 'continent' in africa.columns:
        africa = africa[africa['continent'] == 'Africa']
    else:
        african_countries = [
            'Algeria', 'Nigeria', 'Kenya', 'South Africa', 'Egypt', 'Morocco',
            'Ethiopia', 'Ghana', 'Senegal', 'Tunisia', 'Sudan', 'Angola',
            'Cameroon', 'Ivory Coast', 'Mali', 'Niger', 'Burkina Faso', 'Tanzania',
            'Chad', 'Mozambique', 'Zambia', 'Zimbabwe', 'Rwanda', 'Uganda',
            'Benin', 'Botswana', 'Namibia', 'Malawi', 'Guinea', 'Madagascar',
            'Liberia', 'Sierra Leone', 'Togo', 'Central African Republic',
            'Gambia', 'Lesotho', 'Mauritania', 'Eswatini', 'Djibouti', 'Somalia',
            'Equatorial Guinea', 'Republic of Congo', 'Democratic Republic of the Congo'
        ]
        africa = africa[africa['name'].isin(african_countries)]

    # 🔁 Jointure spatiale
    gdf_sol_with_country = gpd.sjoin(
        gdf_sol,
        africa[['name', 'geometry']],
        how="left",
        predicate="intersects"
    )

    # ✨ Renommage de la colonne
    gdf_sol_with_country.rename(columns={"name": "Country"}, inplace=True)

    # 💾 Sauvegarde du fichier enrichi
    gdf_sol_with_country.drop(columns="geometry").to_csv("soil_profile_africa_with_country.csv", index=False)
    print("✅ Fichier enrichi avec les pays sauvegardé sous : soil_profile_africa_with_country.csv")

except Exception as e:
    print(f"❌ Une erreur s’est produite : {e}")
