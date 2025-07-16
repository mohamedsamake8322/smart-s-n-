import os
import pandas as pd

def nettoyer_fichiers_meteo(
    dossier_source=r"C:\plateforme-agricole-complete-v2\weather_by_country",
    dossier_cible=r"C:\plateforme-agricole-complete-v2\weather_cleaned"
):
    os.makedirs(dossier_cible, exist_ok=True)
    n_total = 0
    n_valides = 0

    for fichier in os.listdir(dossier_source):
        if not fichier.endswith(".csv"):
            continue

        chemin_source = os.path.join(dossier_source, fichier)
        chemin_cible = os.path.join(dossier_cible, fichier)

        try:
            df = pd.read_csv(chemin_source)

            # Vérifie les colonnes requises
            if not {'Longitude', 'Latitude', 'DATE', 'Country'}.issubset(df.columns):
                print(f"❌ {fichier} : colonnes essentielles manquantes, ignoré")
                continue

            n_avant = len(df)

            # Convertit Longitude et Latitude en float, élimine les lignes non convertibles
            df['Longitude'] = pd.to_numeric(df['Longitude'].astype(str).str.replace(".csv", "", regex=False), errors='coerce')
            df['Latitude']  = pd.to_numeric(df['Latitude'].astype(str).str.replace(".csv", "", regex=False), errors='coerce')

            df = df.dropna(subset=['Longitude', 'Latitude'])

            n_apres = len(df)
            n_total += n_avant
            n_valides += n_apres

            df.to_csv(chemin_cible, index=False)
            print(f"✅ {fichier} nettoyé : {n_apres}/{n_avant} lignes conservées")

        except Exception as e:
            print(f"🔥 Erreur dans {fichier} : {e}")

    print(f"\n🧼 Nettoyage terminé : {n_valides} lignes valides sur {n_total} totales")
    print(f"📂 Fichiers corrigés disponibles dans : {dossier_cible}")

# 🔧 Exemple d’usage :
nettoyer_fichiers_meteo()
