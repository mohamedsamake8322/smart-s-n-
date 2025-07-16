import pandas as pd
import os
import numpy as np
from scipy.spatial import cKDTree

# 🧠 Alias pays pour harmonisation
alias_pays = {
    "Algeria": ["Algeria"],
    "Angola": ["Angola"],
    "Benin": ["Benin", "Bénin", "Republic of Benin"],
    "Burkina Faso": ["Burkina", "Burkina Faso"],
    "Cameroon": ["Cameroon", "Cameroun"],
    "Chad": ["Chad"],
    "Congo": ["Congo", "Republic of the Congo", "Democratic Republic of the Congo"],
    "Djibouti": ["Djibouti"],
    "Egypt": ["Egypt", "Arab Republic of Egypt"],
    "Equatorial Guinea": ["Equatorial", "Equatorial Guinea"],
    "Ethiopia": ["Ethiopia"],
    "Gabon": ["Gabon"],
    "Gambia": ["Gambia", "The Gambia"],
    "Ghana": ["Ghana"],
    "Guinea": ["Guinea", "Guinea-Bissau"],
    "Côte d'Ivoire": ["Ivory", "Ivory Coast", "Côte d'Ivoire"],
    "Kenya": ["Kenya"],
    "Malawi": ["Malawi"],
    "Mali": ["Mali"],
    "Mauritania": ["Mauritania"],
    "Morocco": ["Morocco", "Maroc"],
    "Mozambique": ["Mozambique"],
    "Namibia": ["Namibia"],
    "Niger": ["Niger"],
    "Nigeria": ["Nigeria"],
    "Senegal": ["Senegal"],
    "South Africa": ["South", "South Africa"],
    "Sudan": ["Sudan"],
    "Tanzania": ["Tanzania"],
    "Togo": ["Togo"],
    "Uganda": ["Uganda"],
    "Zambia": ["Zambia"],
    "Zimbabwe": ["Zimbabwe"]
}

def normaliser_pays(nom):
    nom = str(nom).strip().lower()
    for canonique, variantes in alias_pays.items():
        if nom == canonique.lower() or nom in [v.lower().strip() for v in variantes]:
            return canonique
    return nom

def fusion_meteo_sol_continental(
    folder_meteo,
    fichier_sol,
    output_path="soil_weather_africa_joined.csv",
    max_distance_deg=0.1
):
    # 📥 Charger sol + nettoyage
    df_sol = pd.read_csv(fichier_sol)
    df_sol['Country'] = df_sol.get('Country', np.nan).apply(normaliser_pays)
    df_sol['soil_Longitude'] = pd.to_numeric(df_sol['Longitude'], errors='coerce').round(4)
    df_sol['soil_Latitude']  = pd.to_numeric(df_sol['Latitude'], errors='coerce').round(4)
    df_sol = df_sol.dropna(subset=['soil_Longitude', 'soil_Latitude'])
    tree = cKDTree(df_sol[['soil_Longitude', 'soil_Latitude']].values)

    all_dfs = []
    total_points = 0

    for file in os.listdir(folder_meteo):
        if not file.endswith(".csv"):
            continue
        path = os.path.join(folder_meteo, file)

        try:
            df_met = pd.read_csv(path)
            if not {'Longitude', 'Latitude', 'Country', 'DATE'}.issubset(df_met.columns):
                print(f"❌ {file} : colonnes essentielles manquantes, ignoré")
                continue

            df_met['Country'] = df_met['Country'].apply(normaliser_pays)
            df_met['Longitude'] = pd.to_numeric(df_met['Longitude'], errors='coerce').round(4)
            df_met['Latitude']  = pd.to_numeric(df_met['Latitude'], errors='coerce').round(4)
            df_met = df_met.dropna(subset=['Longitude', 'Latitude'])

            met_coords = df_met[['Longitude', 'Latitude']].values
            dist, idx = tree.query(met_coords, distance_upper_bound=max_distance_deg)

            valid = dist < max_distance_deg
            if valid.sum() == 0:
                print(f"⚠️ {file} : aucun point météo matché avec le sol à {max_distance_deg}°")
                continue

            df_met_valid = df_met.iloc[np.where(valid)[0]].reset_index(drop=True)
            df_sol_match = df_sol.iloc[idx[valid]].reset_index(drop=True)

            df_fusion = pd.concat([df_sol_match, df_met_valid], axis=1)
            pays_fusionnes = df_met_valid['Country'].unique()
            print(f"✅ {file} fusionné : {len(df_met_valid)} points | Pays : {', '.join(pays_fusionnes)}")

            all_dfs.append(df_fusion)
            total_points += len(df_met_valid)

        except Exception as e:
            print(f"🔥 Erreur dans {file} : {e}")

    # 📦 Fusion finale
    if not all_dfs:
        print("⚠️ Aucun fichier météo n’a pu être fusionné — vérifie la couverture spatiale et les noms de pays.")
        return pd.DataFrame()

    df_final = pd.concat(all_dfs, ignore_index=True)
    df_final.to_csv(output_path, index=False)
    print(f"\n✅ Fusion continentale terminée → {output_path}")
    print(f"📌 Points couverts : {total_points} | Pays inclus : {df_final['Country'].nunique()}")

    return df_final

# 🔧 Exemple d’usage
fusion_meteo_sol_continental(
    folder_meteo=r"C:\plateforme-agricole-complete-v2\weather_cleaned",
    fichier_sol=r"C:\plateforme-agricole-complete-v2\soil_profile_africa_with_country.csv",
    max_distance_deg=0.1
)
