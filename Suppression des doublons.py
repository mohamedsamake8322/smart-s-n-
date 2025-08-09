import pandas as pd

file_in = r"C:\plateforme-agricole-complete-v2\SmartSènè\fusion_finale_clean.csv"
file_out = r"C:\plateforme-agricole-complete-v2\SmartSènè\fusion_finale_clean_dedup.csv"

print("📥 Chargement du fichier fusionné...")
df = pd.read_csv(file_in)

print(f"Shape initial : {df.shape}")

# 1. Supprimer doublons exacts sur toutes colonnes (exclut les doublons ligne à ligne)
df = df.drop_duplicates()
print(f"Après suppression doublons exacts : {df.shape}")

# 2. Supprimer doublons sur la clé (country, year) en gardant la première occurrence
dups = df.duplicated(subset=["country", "year"])
print(f"Doublons sur (country, year) : {dups.sum()}")
if dups.sum() > 0:
    df = df.drop_duplicates(subset=["country", "year"], keep='first')
    print(f"Après suppression doublons (country, year) : {df.shape}")

# 3. Filtrer années aberrantes hors [1900, 2100]
mask_years = (df["year"] >= 1900) & (df["year"] <= 2100)
print(f"Lignes années aberrantes (hors [1900,2100]) : {(~mask_years).sum()}")
df = df.loc[mask_years]
print(f"Après filtrage années aberrantes : {df.shape}")

# 4. Vérifier valeurs négatives rainfall (à supprimer ou traiter si besoin)
if "rainfall" in df.columns:
    neg_rainfall = df[df["rainfall"] < 0]
    print(f"Valeurs négatives rainfall : {len(neg_rainfall)}")
    # Par exemple on peut supprimer ces lignes :
    df = df[df["rainfall"] >= 0]
    print(f"Après suppression rainfall négatif : {df.shape}")

# 5. Sauvegarder le dataset nettoyé
df.to_csv(file_out, index=False)
print(f"✅ Nettoyage terminé. Fichier sauvegardé : {file_out}")
