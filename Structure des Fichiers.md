SMAP_SoilMoisture_Mali.csv (['system:index', 'ADM0_CODE', 'ADM0_NAME', 'ADM1_CODE', 'ADM1_NAME',
 'DISP_AREA', 'EXP1_YEAR', 'STATUS', 'STR1_YEAR',
 'Shape_Area', 'Shape_Leng', 'mean', '.geo']
)

WorldClim BIO MLI Variables V1.csv (🔹 Colonnes du fichier :
['system:index', 'ADM0_CODE', 'ADM0_NAME', 'ADM1_CODE', 'ADM1_NAME', 'DISP_AREA', 'EXP1_YEAR', 'STATUS', 'STR1_YEAR', 'Shape_Area', 'Shape_Leng', 'bio01', 'bio02', 'bio03', 'bio04', 'bio05', 'bio06', 'bio07', 'bio08', 'bio09', 'bio10', 'bio11', 'bio12', 'bio13', 'bio14', 'bio15', 'bio16', 'bio17', 'bio18', 'bio19', '.geo'])
WorldClim Mali Monthly V1.csv(🔹 Colonnes du fichier :
['system:index', 'ADM0_CODE', 'ADM0_NAME', 'ADM1_CODE', 'ADM1_NAME', 'DISP_AREA', 'EXP1_YEAR', 'STATUS', 'STR1_YEAR', 'Shape_Area', 'Shape_Leng', 'prec', 'tavg', 'tmax', 'tmin', '.geo'])
CHIRPS_SMAP_DAILY_PENTMli.csv(🔹 Colonnes du fichier :
['system:index', 'ADM0_CODE', 'ADM0_NAME', 'ADM1_CODE', 'ADM1_NAME', 'CHIRPS_Daily', 'CHIRPS_Pentad', 'DISP_AREA', 'EXP1_YEAR', 'SMAP_SoilMoisture', 'STATUS', 'STR1_YEAR', 'Shape_Area', 'Shape_Leng', '.geo'] )
GEDI_Mangrove_CSV_Mali_Single.csv(🔹 Colonnes du fichier :
['system:index', 'ADM0_NAME', 'ADM1_NAME', 'GEDI_CanopyHeight', 'Mangrove2000', 'TidalWetlands2019', '.geo'])









Pour recoonaitre la structre
import pandas as pd

# Charger le fichier CSV
fichier = r"C:\Users\moham\Music\Boua\GEDI_Mangrove_CSV_Mali_Single.csv"
df = pd.read_csv(fichier)

# Afficher la structure générale
print("🔹 Colonnes du fichier :")
print(df.columns.tolist())
print("\n🔹 Aperçu des 5 premières lignes :")
print(df.head())

# Nombre de lignes et colonnes
print("\n🔹 Dimensions du fichier :", df.shape)

# Vérification des valeurs manquantes
print("\n🔹 Valeurs manquantes par colonne :")
print(df.isna().sum())

# Statistiques générales
print("\n🔹 Statistiques descriptives :")
print(df.describe(include="all"))



Pour Fusionner les chiers climat et sol


import pandas as pd
import glob
import os

# ----------------------------
# 1️⃣ Charger et fusionner tous les fichiers CSV
# ----------------------------
folder = r"C:\Users\moham\Music\Boua"  # chemin vers tes fichiers CSV
csv_files = glob.glob(os.path.join(folder, "*.csv"))

dfs = []
for file in csv_files:
    df = pd.read_csv(file)

    # Extraire le nom du pays à partir du fichier
    country_name = os.path.basename(file).split("_")[-1].replace(".csv","")
    df["country"] = country_name

    dfs.append(df)

# Fusionner tous les DataFrames (union des colonnes)
merged_df = pd.concat(dfs, axis=0, ignore_index=True, sort=False)

# ----------------------------
# 2️⃣ Supprimer colonnes inutiles
# ----------------------------
cols_to_drop = ["Mangrove2000", ".geo", "system:index"]
merged_df = merged_df.drop(columns=[c for c in cols_to_drop if c in merged_df.columns])

# ----------------------------
# 3️⃣ Gérer les NaN
# ----------------------------
# Option 1 : Remplacer NaN par 0 pour les variables explicatives
merged_df.fillna(0, inplace=True)

# Option 2 (si tu veux ne garder que les lignes où la cible est connue)
# merged_df = merged_df[merged_df["mean"].notna()]

# ----------------------------
# 4️⃣ Préparer les colonnes pour XGBoost
# ----------------------------
# Variable cible
target_col = "mean"

# Colonnes explicatives : toutes sauf cible et pays
feature_cols = [c for c in merged_df.columns if c != target_col and c != "country" and c != "ADM0_NAME" and c != "ADM1_NAME"]

X = merged_df[feature_cols]
y = merged_df[target_col]

# ----------------------------
# 5️⃣ Sauvegarder le dataset final
# ----------------------------
output_file = os.path.join(folder, "Merged_XGBoost_Dataset.csv")
merged_df.to_csv(output_file, index=False)

print(f"✅ Fusion terminée ! Dataset prêt pour XGBoost : {output_file}")
print(f"Dimensions finales : {merged_df.shape}")
print("Aperçu des colonnes :", merged_df.columns.tolist())






Fusuion complète
import pandas as pd
import glob
import os

# Dossier contenant tes CSVs
folder_path = r"C:\Users\moham\Music\Boua"
all_files = glob.glob(os.path.join(folder_path, "*.csv"))

dfs = []

for file in all_files:
    print(f"📄 Lecture du fichier : {file}")
    # Lecture avec dtype=object pour éviter les conflits et low_memory=False
    df = pd.read_csv(file, dtype=object, low_memory=False)

    # Supprimer les colonnes volumineuses ou inutiles
    cols_to_drop = ["Mangrove2000", ".geo", "system:index"]
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    # Ajouter le dataframe à la liste
    dfs.append(df)

# Fusionner tous les fichiers
merged_df = pd.concat(dfs, axis=0, ignore_index=True, sort=False)
print(f"✅ Fusion terminée ! Dimensions : {merged_df.shape}")

# Conversion des colonnes numériques après fusion
non_numeric_cols = ['ADM0_NAME', 'ADM1_NAME', 'ADM2_NAME', 'country'] if 'ADM2_NAME' in merged_df.columns else ['ADM0_NAME', 'ADM1_NAME', 'country']
num_cols = [c for c in merged_df.columns if c not in non_numeric_cols]

merged_df[num_cols] = merged_df[num_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

# Sauvegarder le dataset fusionné
output_file = os.path.join(folder_path, "Merged_XGBoost_Dataset.csv")
merged_df.to_csv(output_file, index=False)
print(f"✅ Dataset prêt pour XGBoost : {output_file}")












import pandas as pd

# -----------------------------
# Chemins des fichiers
# -----------------------------
ndvi_file = r"C:\Downloads\New folder (2)\NDVI_NDMI_Mali_2021_2024_merged.csv"
faostat_file = r"C:\Downloads\New folder (2)\merged_all_advanced.csv"
smap_file = r"C:\Downloads\New folder (2)\SMAP_SoilMoisture_Mali.csv"
worldclim_bio_file = r"C:\Downloads\New folder (2)\WorldClim BIO MLI Variables V1.csv"
worldclim_monthly_file = r"C:\Downloads\New folder (2)\WorldClim Mali Monthly V1.csv"
chirps_smap_file = r"C:\Downloads\New folder (2)\CHIRPS_SMAP_DAILY_PENTMli.csv"
gedi_file = r"C:\Downloads\New folder (2)\GEDI_Mangrove_CSV_Mali_Single.csv"

# -----------------------------
# Charger les fichiers CSV
# -----------------------------
print("Chargement des fichiers...")
ndvi_df = pd.read_csv(ndvi_file)
faostat_df = pd.read_csv(faostat_file, low_memory=False)  # Evite les warnings
smap_df = pd.read_csv(smap_file)
worldclim_bio_df = pd.read_csv(worldclim_bio_file)
worldclim_monthly_df = pd.read_csv(worldclim_monthly_file)
chirps_smap_df = pd.read_csv(chirps_smap_file)
gedi_df = pd.read_csv(gedi_file)

# -----------------------------
# Harmoniser les colonnes clés
# -----------------------------
# FAOSTAT : ajouter ADM0_NAME et renommer Area -> ADM1_NAME
if "ADM0_NAME" not in faostat_df.columns:
    faostat_df["ADM0_NAME"] = "Mali"
faostat_df = faostat_df.rename(columns={"Area": "ADM1_NAME", "Year": "Year"})

# NDVI : renommer year -> Year, month -> Month
ndvi_df = ndvi_df.rename(columns={"year": "Year", "month": "Month"})

# SMAP, WorldClim, CHIRPS : EXP1_YEAR -> Year
for df in [smap_df, worldclim_bio_df, worldclim_monthly_df, chirps_smap_df]:
    df.rename(columns={"EXP1_YEAR": "Year"}, inplace=True)

# -----------------------------
# Sélection des colonnes utiles pour éviter les doublons
# -----------------------------
# SMAP
smap_df = smap_df[["ADM0_NAME","ADM1_NAME","Year","mean"]]

# WorldClim BIO
worldclim_bio_df = worldclim_bio_df[["ADM0_NAME","ADM1_NAME","Year"] + [f"bio{i:02d}" for i in range(1,20)]]

# WorldClim Monthly
worldclim_monthly_df = worldclim_monthly_df[["ADM0_NAME","ADM1_NAME","Year","prec","tavg","tmax","tmin"]]

# CHIRPS + SMAP
chirps_smap_df = chirps_smap_df[["ADM0_NAME","ADM1_NAME","Year","CHIRPS_Daily","CHIRPS_Pentad","SMAP_SoilMoisture"]]

# GEDI
gedi_df = gedi_df[["ADM0_NAME","ADM1_NAME","GEDI_CanopyHeight","Mangrove2000","TidalWetlands2019"]]

# -----------------------------
# Fusionner les fichiers progressivement
# -----------------------------
print("Fusion NDVI + FAOSTAT...")
df_merged = pd.merge(ndvi_df, faostat_df, how="outer", on=["ADM0_NAME", "ADM1_NAME", "Year"])

print("Fusion avec SMAP...")
df_merged = pd.merge(df_merged, smap_df, how="outer", on=["ADM0_NAME", "ADM1_NAME", "Year"])

print("Fusion avec WorldClim BIO...")
df_merged = pd.merge(df_merged, worldclim_bio_df, how="outer", on=["ADM0_NAME", "ADM1_NAME", "Year"])

print("Fusion avec WorldClim Monthly...")
df_merged = pd.merge(df_merged, worldclim_monthly_df, how="outer", on=["ADM0_NAME", "ADM1_NAME", "Year"])

print("Fusion avec CHIRPS + SMAP...")
df_merged = pd.merge(df_merged, chirps_smap_df, how="outer", on=["ADM0_NAME", "ADM1_NAME", "Year"])

print("Fusion avec GEDI...")
df_merged = pd.merge(df_merged, gedi_df, how="left", on=["ADM0_NAME", "ADM1_NAME"])  # pas d'année

# -----------------------------
# Résumé final
# -----------------------------
print("Fusion terminée !")
print(f"Colonnes finales : {df_merged.columns.tolist()}")
print(f"Nombre de lignes : {len(df_merged)}")

# -----------------------------
# Sauvegarder le dataset global
# -----------------------------
output_file = r"C:\Downloads\New folder (2)\Mali_Global_Dataset.csv"
df_merged.to_csv(output_file, index=False)
print(f"Dataset global sauvegardé : {output_file}")
