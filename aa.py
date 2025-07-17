import pandas as pd

# 📥 Charger le fichier
df_soil = pd.read_csv("iSDA_soil_data.csv")

# 🧠 Aperçu du tableau
print("Nombre de lignes :", len(df_soil))
print("Colonnes disponibles :")
print(df_soil.columns.tolist())

# 🔎 Vérifier les valeurs manquantes
missing = df_soil.isnull().sum()
print("Variables avec données manquantes :")
print(missing[missing > 0])

# 🗺️ Vérifier la couverture géographique
print("Coordonnées min/max :")
print("Longitude :", df_soil['longitude'].min(), "-", df_soil['longitude'].max())
print("Latitude :", df_soil['latitude'].min(), "-", df_soil['latitude'].max())
