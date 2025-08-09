import pandas as pd
import os

# 📂 Chemin du dossier contenant les fichiers
base_path = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# 📜 Liste des fichiers CSV à analyser
fichiers = [
    "Soil_AllLayers_AllAfrica-002.csv",
    "GEDI_Mangrove_CSV.csv",
    "CHIRPS_DAILY_PENTAD.csv",
    "SMAP_SoilMoisture.csv",
    "WorldClim BIO Variables V1.csv",
    "WAPOR_All_Variables_Merged.csv",
    "NDMI_Afrique_fusionné.csv",
    "WorldClim_Monthly_Fusion.csv"
]

colonnes_communes = None

for fichier in fichiers:
    chemin = os.path.join(base_path, fichier)
    try:
        df = pd.read_csv(chemin)
        print(f"\n📄 Fichier : {fichier}")
        print(f"   Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes")
        print(f"   Colonnes : {list(df.columns[:10])}...")  # On affiche les 10 premières
        print(f"   Types :\n{df.dtypes.head(5)}")

        # Comparaison colonnes communes
        if colonnes_communes is None:
            colonnes_communes = set(df.columns)
        else:
            colonnes_communes &= set(df.columns)
    except Exception as e:
        print(f"❌ Erreur lecture {fichier} : {e}")

print("\n🔍 Colonnes communes à tous les fichiers :", colonnes_communes if colonnes_communes else "Aucune")
