import pandas as pd
import os

# Chemins des fichiers
fichier_sol = r"C:\plateforme-agricole-complete-v2\soil_profile_africa_with_country.csv"
folder_meteo = r"C:\plateforme-agricole-complete-v2\weather_cleaned"

# Chargement des données sol
df_sol = pd.read_csv(fichier_sol)

# Extraire les pays disponibles dans les données sol
pays_sol = df_sol['Country'].dropna().unique().tolist()

# Parcourir les fichiers météo
for file in os.listdir(folder_meteo):
    if not file.endswith(".csv"):
        continue

    # Extraire le nom du pays à partir du nom du fichier météo
    nom_pays_meteo = file.replace("weather_", "").replace(".csv", "")

    # Chargement du fichier météo
    path = os.path.join(folder_meteo, file)
    df_met = pd.read_csv(path)

    nb_met = len(df_met)
    nb_sol = df_sol[df_sol['Country'].str.lower().str.contains(nom_pays_meteo.lower())].shape[0]

    if nb_met == 0:
        print(f"❌ {nom_pays_meteo} → 0 point météo (fichier vide)")
    elif nb_sol == 0:
        print(f"⚠️ {nom_pays_meteo} → météo : {nb_met} points / sol : 0 points (aucun point sol associé)")
    else:
        print(f"✅ {nom_pays_meteo} → météo : {nb_met} points / sol : {nb_sol} points")

print("\n📌 Vérification terminée.")
