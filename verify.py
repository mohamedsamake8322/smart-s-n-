import pandas as pd
import os

# 📁 Chemin du fichier fusionné
final_path = r"C:\plateforme-agricole-complete-v2\SmartSènè\Fusion_agronomique_intelligente_final.csv.gz"

# 📥 Chargement du fichier
print("📥 Chargement du fichier fusionné...")
df = pd.read_csv(final_path, compression="gzip")

# 📊 Dimensions du fichier
print("\n📊 Dimensions du fichier fusionné :")
print(f"- Nombre de lignes : {len(df):,}")
print(f"- Nombre de colonnes : {len(df.columns)}")

# 📋 Liste des colonnes
print("\n📋 Colonnes présentes :")
for col in df.columns:
    print(f"  - {col}")

# ✅ Dimensions attendues (selon pandas)
expected_rows = 1573200
expected_cols = 93

# 🔍 Comparaison
print("\n🔍 Comparaison avec les dimensions pandas :")
if len(df) == expected_rows:
    print(f"✅ Nombre de lignes correct : {expected_rows:,}")
else:
    print(f"⚠️ Nombre de lignes différent : {len(df):,} vs attendu {expected_rows:,}")

if len(df.columns) == expected_cols:
    print(f"✅ Nombre de colonnes correct : {expected_cols}")
else:
    print(f"⚠️ Nombre de colonnes différent : {len(df.columns)} vs attendu {expected_cols}")

# 🧠 Colonnes attendues (à adapter si besoin)
expected_columns = [
    # Ajoute ici ta liste de 93 colonnes attendues si tu veux une comparaison plus fine
]

# 📌 Comparaison des colonnes (si liste fournie)
if expected_columns:
    missing = [col for col in expected_columns if col not in df.columns]
    extra = [col for col in df.columns if col not in expected_columns]

    print("\n📌 Colonnes manquantes :", missing if missing else "Aucune")
    print("📌 Colonnes en trop :", extra if extra else "Aucune")
