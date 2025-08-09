import pandas as pd

file_path = r"C:\plateforme-agricole-complete-v2\SmartSènè\fusion_finale_clean_dedup.csv"

print("📥 Chargement du fichier nettoyé...")
df = pd.read_csv(file_path)

print(f"\n📊 Dimensions du dataset : {df.shape}")

# 1. Doublons sur (country, year)
print("\n🔎 Vérification des doublons sur (country, year)...")
dups = df.duplicated(subset=["country", "year"])
print(f"Nombre de doublons détectés : {dups.sum()}")
if dups.sum() > 0:
    print("Exemples de doublons :")
    print(df[dups].head())

# 2. Vérification années aberrantes
print("\n🔎 Vérification des années aberrantes (hors 1900-2100)...")
aberrant_years = df[(df["year"] < 1900) | (df["year"] > 2100)]
print(f"Nombre de lignes avec années aberrantes : {len(aberrant_years)}")
if len(aberrant_years) > 0:
    print(aberrant_years[["country", "year"]].drop_duplicates())

# 3. Statistiques descriptives variables clés
print("\n📊 Statistiques descriptives variables clés :")
for col in ["rainfall", "soil_moisture"]:
    if col in df.columns:
        print(f"\nVariable : {col}")
        print(df[col].describe())

# 4. Vérification valeurs négatives (ex: rainfall)
print("\n🔎 Vérification des valeurs négatives (rainfall)...")
if "rainfall" in df.columns:
    negs = df[df["rainfall"] < 0]
    print(f"Nombre de valeurs négatives dans rainfall : {len(negs)}")
    if len(negs) > 0:
        print(negs[["country", "year", "rainfall"]])

# 5. Valeurs manquantes par colonne
print("\n🔍 Nombre de valeurs manquantes par colonne :")
print(df.isna().sum())

# 6. Distribution lignes par pays
print("\n🌍 Nombre de lignes par pays :")
print(df["country"].value_counts())

# 7. Distribution lignes par année
print("\n📆 Nombre de lignes par année :")
print(df["year"].value_counts().sort_index())

print("\n✅ Rapport de validation terminé.")
