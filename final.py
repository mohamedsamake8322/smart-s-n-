import pandas as pd
import os
import numpy as np
from scipy.spatial import cKDTree

# 🧠 Alias pays pour normalisation
alias_pays = {
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

def fusion_par_pays(
    folder_meteo,
    fichier_sol,
    dossier_sortie="fusion_par_pays",
    rayon_deg=0.1
):
    os.makedirs(dossier_sortie, exist_ok=True)

    # 🧱 Charger sol avec coordonnées
    df_sol = pd.read_csv(fichier_sol)
    df_sol['Country'] = df_sol.get('Country', np.nan).apply(normaliser_pays)
    df_sol['soil_Longitude'] = pd.to_numeric(df_sol['Longitude'], errors='coerce').round(4)
    df_sol['soil_Latitude'] = pd.to_numeric(df_sol['Latitude'], errors='coerce').round(4)
    df_sol = df_sol.dropna(subset=['soil_Longitude', 'soil_Latitude'])
    sol_tree = cKDTree(df_sol[['soil_Longitude', 'soil_Latitude']].values)

    for fichier in os.listdir(folder_meteo):
        if not fichier.endswith(".csv"):
            continue
        chemin = os.path.join(folder_meteo, fichier)
        try:
            df_met = pd.read_csv(chemin)
            if not {'Longitude', 'Latitude', 'Country', 'DATE'}.issubset(df_met.columns):
                print(f"❌ {fichier} : colonnes manquantes, ignoré")
                continue

            pays_nom = normaliser_pays(df_met['Country'].iloc[0])
            df_met['Longitude'] = pd.to_numeric(df_met['Longitude'], errors='coerce').round(4)
            df_met['Latitude'] = pd.to_numeric(df_met['Latitude'], errors='coerce').round(4)
            df_met = df_met.dropna(subset=['Longitude', 'Latitude'])

            met_coords = df_met[['Longitude', 'Latitude']].values
            dist, idx = sol_tree.query(met_coords, distance_upper_bound=rayon_deg)
            valid = dist < rayon_deg
            if valid.sum() == 0:
                print(f"⚠️ {pays_nom} : aucun point matché avec le sol")
                continue

            df_met_valid = df_met.iloc[np.where(valid)[0]].copy()
            df_sol_match = df_sol.iloc[idx[valid]].copy()

            df_met_valid.reset_index(drop=True, inplace=True)
            df_sol_match.reset_index(drop=True, inplace=True)
            df_sol_match = df_sol_match.add_prefix("soil_")

            df_fusion = pd.concat([df_sol_match, df_met_valid], axis=1)
            chemin_sortie = os.path.join(dossier_sortie, f"soil_weather_joined_{pays_nom}.csv")
            df_fusion.to_csv(chemin_sortie, index=False)
            print(f"✅ {pays_nom} fusionné : {len(df_fusion)} points → {chemin_sortie}")

        except Exception as e:
            print(f"🔥 Erreur {fichier} : {e}")

# 🔧 Exemple d’usage :
fusion_par_pays(
    folder_meteo = r"C:\plateforme-agricole-complete-v2\weather_cleaned",
    fichier_sol  = r"C:\plateforme-agricole-complete-v2\soil_profile_africa_with_country.csv",
    dossier_sortie = r"C:\plateforme-agricole-complete-v2\fusion_par_pays",
    rayon_deg=0.1
)
