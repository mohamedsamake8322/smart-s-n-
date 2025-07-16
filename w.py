#💻 Script proposé : Jointure par proximité avec KDTree (rapide et scalable)
import pandas as pd
from sklearn.neighbors import KDTree

def join_soil_weather(soil_csv, weather_csv, max_distance_km=5):
    # Charger les fichiers
    soil_df = pd.read_csv(soil_csv)
    weather_df = pd.read_csv(weather_csv)

    # Garder seulement les colonnes météo + coords
    weather_vars = [col for col in weather_df.columns if col not in ['Country', 'DATE']]
    weather_subset = weather_df.dropna(subset=['Latitude', 'Longitude'])[weather_vars + ['Latitude', 'Longitude']]

    # Construire l’arbre pour recherche rapide
    tree = KDTree(weather_subset[['Latitude', 'Longitude']], metric='euclidean')

    # Trouver l’indice du point météo le plus proche
    distances, indices = tree.query(soil_df[['Latitude', 'Longitude']], k=1)

    # Filtrer les appariements trop éloignés
    threshold_deg = max_distance_km / 111  # approx. conversion km → degrés
    matched = distances[:, 0] <= threshold_deg
    soil_df_matched = soil_df[matched].copy()
    weather_matched = weather_subset.iloc[indices[matched, 0]].reset_index(drop=True)

    # Fusionner
    combined_df = pd.concat([soil_df_matched.reset_index(drop=True), weather_matched], axis=1)

    # Sauvegarde
    combined_df.to_csv("soil_weather_africa_joined.csv", index=False)
    print("✅ Fusion sol+météo terminée : soil_weather_africa_joined.csv")

    return combined_df

# Exemple d’usage :
soil_weather = join_soil_weather(
    "soil_profile_africa_reprojected.csv",
    "weather_africa_cleaned_filtered.csv",
    max_distance_km=5
)
