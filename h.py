import pandas as pd

# Chemin du fichier
fichier = r"C:\plateforme-agricole-complete-v2\SmartSènè\X_land_water_cleanedRessources en terres et en eau.csv"

# Lecture partielle pour voir la structure
df_sample = pd.read_csv(fichier, nrows=10)  # juste les 10 premières lignes
print("Aperçu des données :")
print(df_sample)

# Lecture seulement des noms de colonnes
colonnes = pd.read_csv(fichier, nrows=0).columns
print("\nColonnes :", list(colonnes))

# Taille totale (sans charger tout en mémoire)
import os
taille_mo = os.path.getsize(fichier) / (1024*1024)
print(f"\nTaille du fichier : {taille_mo:.2f} Mo")
