import pandas as pd

# Chemin vers le fichier fusionné nettoyé
file_path = r"C:\plateforme-agricole-complete-v2\SmartSènè\fusion_finale_clean.csv"

print("📥 Chargement du fichier fusionné nettoyé...")
df = pd.read_csv(file_path)

print(f"📊 Dimensions du dataset : {df.shape}")

# 1. Vérifier doublons sur la clé (country, year)
print("\n🔎 Vérification des doublons sur (country, year)...")
duplicates = df.duplicated(subset=["country", "year"])
print(f"Nombre de doublons détectés : {duplicates.sum()}")
if duplicates.sum() > 0:
    print("Exemple de doublons :")
    print(df[duplicates].head())

# 2. Vérifier années aberrantes (exemple ici 1000)
print("\n🔎 Vérification des années aberrantes (valeurs < 1900 ou > 2100)...")
aberrant_years = df[(df["year"] < 1900) | (df["year"] > 2100)]
print(f"Nombre de lignes avec années aberrantes : {len(aberrant_years)}")
if len(aberrant_years) > 0:
    print(aberrant_years[["country", "year"]].drop_duplicates())

# 3. Statistiques descriptives avant/après fusion pour variables clés
# Si tu as un fichier source original, il faut charger ici pour comparer,
# sinon on compare simplement la cohérence interne.

print("\n📊 Statistiques descriptives des variables clés (ex: rainfall, soil_moisture)...")
for col in ["rainfall", "soil_moisture"]:
    if col in df.columns:
        print(f"\nVariable : {col}")
        print(df[col].describe())

# 4. Contrôle de valeurs négatives (exemple rainfall)
if "rainfall" in df.columns:
    negatives = df[df["rainfall"] < 0]
    print(f"\n🔎 Nombre de valeurs négatives dans rainfall : {len(negatives)}")

# 5. Intégrité géographique - si colonnes lat/lon présentes (optionnel)
if "lat" in df.columns and "lon" in df.columns:
    print("\n🌍 Vérification de la validité des coordonnées lat/lon...")
    invalid_coords = df[(df["lat"] < -90) | (df["lat"] > 90) | (df["lon"] < -180) | (df["lon"] > 180)]
    print(f"Nombre de coordonnées invalides : {len(invalid_coords)}")

# 6. Statistiques générales (valeurs manquantes par colonne)
print("\n🔍 Nombre de valeurs manquantes par colonne :")
print(df.isna().sum())

print("\n✅ Vérifications terminées.")
