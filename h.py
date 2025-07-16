import pandas as pd
import os

# Chemins des fichiers
fichier_sol = r"C:\plateforme-agricole-complete-v2\soil_profile_africa_with_country.csv"
folder_meteo = r"C:\plateforme-agricole-complete-v2\weather_cleaned"

# Chargement des données sol
df_sol = pd.read_csv(fichier_sol)
pays_sol = df_sol['Country'].dropna().unique().tolist()

# 🧠 Table d’alias météo → noms dans sol
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
    "Malaysia": [],  # ❌ Non africain
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

# 🔍 Inspection pays par pays
for file in os.listdir(folder_meteo):
    if not file.endswith(".csv"):
        continue

    nom_pays_meteo = file.replace("weather_", "").replace(".csv", "")
    path = os.path.join(folder_meteo, file)
    df_met = pd.read_csv(path)
    nb_met = len(df_met)

    aliases = alias_map.get(nom_pays_meteo, [nom_pays_meteo])
    df_sol_match = df_sol[df_sol['Country'].apply(lambda x: any(alias.lower() in str(x).lower() for alias in aliases))]
    nb_sol = len(df_sol_match)

    if nb_met == 0:
        print(f"❌ {nom_pays_meteo} → 0 point météo (fichier vide)")
    elif nb_sol == 0:
        print(f"⚠️ {nom_pays_meteo} → météo : {nb_met} points / sol : 0 points (nom non reconnu dans sol)")
    else:
        print(f"✅ {nom_pays_meteo} → météo : {nb_met} points / sol : {nb_sol} points")

print("\n📌 Diagnostic terminé.")
