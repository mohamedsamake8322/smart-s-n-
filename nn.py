import pandas as pd
import os
import numpy as np
from scipy.spatial import cKDTree

# Table d’alias météo → noms sol
alias_map = {
    "Angola": ["Angola"],
    "Benin": ["Benin", "Bénin", "Republic of Benin"],
    "Burkina": ["Burkina Faso"],
    "Cameroon": ["Cameroon", "Cameroun"],
    "Chad": ["Chad"],
    "Congo": ["Congo", "Republic of the Congo", "Democratic Republic of the Congo"],
    "Djibouti": ["Djibouti"],
    "Egypt": ["Egypt", "Arab Republic of Egypt"],
    "Equatorial": ["Equatorial Guinea"],
    "Ethiopia": ["Ethiopia"],
    "Gabon": ["Gabon"],
    "Gambia": ["Gambia", "The Gambia"],
    "Ghana": ["Ghana"],
    "Guinea": ["Guinea", "Guinea-Bissau"],
    "Ivory": ["Côte d'Ivoire", "Ivory Coast"],
    "Kenya": ["Kenya"],
    "Malawi": ["Malawi"],
    "Malaysia": [],  # Exclure
    "Mali": ["Mali"],
    "Mauritania": ["Mauritania"],
    "Morocco": ["Morocco", "Maroc"],
    "Mozambique": ["Mozambique"],
    "Namibia": ["Namibia"],
    "Niger": ["Niger"],
    "Nigeria": ["Nigeria"],
    "Senegal": ["Senegal"],
    "South": ["South Africa"],
    "Sudan": ["Sudan"],
    "Tanzania": ["Tanzania"],
    "Togo": ["Togo"],
    "Uganda": ["Uganda"],
    "Zambia": ["Zambia"],
    "Zimbabwe": ["Zimbabwe"]
}

def match_country(sol_df, meteo_name):
    aliases = alias_map.get(meteo_name, [meteo_name])
    return sol_df[sol_df['Country'].apply(lambda x: any(alias.lower() in str(x).lower() for alias in aliases))]

def fusion_meteo_sol_continental(folder_meteo, fichier_sol, output_path="soil_weather_africa_joined.csv", max_distance_deg=0.3):
    print("🔁 Lancement de la fusion météo-sol avec rayon :", max_distance_deg)

    df_sol_all = pd.read_csv(fichier_sol)
    df_sol_all['soil_Longitude'] = pd.to_numeric(df_sol_all['Longitude'], errors='coerce').round(4)
    df_sol_all['soil_Latitude']  = pd.to_numeric(df_sol_all['Latitude'], errors='coerce').round(4)
    df_sol_all = df_sol_all.dropna(subset=['soil_Longitude', 'soil_Latitude'])

    all_dfs = []
    total_files = 0

    for file in os.listdir(folder_meteo):
        if not file.endswith(".csv"):
            continue
        total_files += 1
        meteo_name = file.replace("weather_", "").replace(".csv", "")
        path = os.path.join(folder_meteo, file)

        print(f"\n📂 Fichier météo détecté : {file}")

        try:
            df_met = pd.read_csv(path)
            print(f"🧮 Points météo : {len(df_met)}")

            if not {'Longitude', 'Latitude', 'Country', 'DATE'}.issubset(df_met.columns):
                print(f"❌ Colonnes essentielles manquantes")
                continue

            df_met['Longitude'] = pd.to_numeric(df_met['Longitude'], errors='coerce').round(4)
            df_met['Latitude']  = pd.to_numeric(df_met['Latitude'], errors='coerce').round(4)
            df_met = df_met.dropna(subset=['Longitude', 'Latitude'])

            if df_met.empty:
                print("⚠️ Fichier météo vide")
                continue

            df_sol_match = match_country(df_sol_all, meteo_name)
            print(f"🌱 Points sol matchés sur le pays '{meteo_name}': {len(df_sol_match)}")

            if df_sol_match.empty:
                print(f"⚠️ Aucun point sol trouvé pour ce pays")
                continue

            tree = cKDTree(df_sol_match[['soil_Longitude', 'soil_Latitude']].values)
            met_coords = df_met[['Longitude', 'Latitude']].values
            dist, idx = tree.query(met_coords, distance_upper_bound=max_distance_deg)

            valid = dist < max_distance_deg
            print(f"🔎 Points météo matchés dans le rayon : {valid.sum()}")

            if valid.sum() == 0:
                print(f"⚠️ Aucun point météo dans le rayon pour ce pays")
                continue

            df_met_valid = df_met.iloc[np.where(valid)[0]].reset_index(drop=True)
            df_sol_valid = df_sol_match.iloc[idx[valid]].reset_index(drop=True)
            df_fusion = pd.concat([df_sol_valid, df_met_valid], axis=1)
            pays_fusionnes = df_met_valid['Country'].unique()
            print(f"✅ Fusion réussie : {len(df_met_valid)} lignes | Pays météo : {', '.join(pays_fusionnes)}")

            all_dfs.append(df_fusion)

        except Exception as e:
            print(f"🔥 Erreur dans {file} : {e}")

    # Fusion finale
    all_dfs = [df.reset_index(drop=True) for df in all_dfs]
    if all_dfs:
        df_final = pd.concat(all_dfs, ignore_index=True)
        df_final.to_csv(output_path, index=False)
        print(f"\n🎯 Fusion terminée → {output_path}")
        print(f"📊 Total fichiers traités : {total_files}")
        print(f"📌 Total lignes fusionnées : {len(df_final)} | Pays inclus : {df_final['Country'].nunique()}")
    else:
        print("\n❌ Aucun fichier météo n’a pu être fusionné.")
