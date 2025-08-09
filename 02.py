import pandas as pd
import os

# Dossier contenant les fichiers
base_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè\Fichier pour l'entrainement de xgboost"

# Liste des fichiers à traiter
files_info = {
    "FAOSTAT_CHIRPS_SMAP_merged.csv.gz": ['country', 'year'],  # clés typiques FAO
    "X_enriched_plus_GEDI_spatial.csv.gz": ['lon', 'lat'],     # clés spatiales
    "fusion_finale.csv.gz": ['country', 'year'],               # similaire FAOSTAT
    "Fusion_agronomique_intelligente_final.csv.gz": ['Area', 'Year']  # clé possible à vérifier
}

for filename, key_cols in files_info.items():
    print(f"\n\n=== Traitement du fichier : {filename} ===")
    path = os.path.join(base_dir, filename)

    # Chargement
    df = pd.read_csv(path, compression='gzip')
    print(f"📥 Chargé {len(df)} lignes et {len(df.columns)} colonnes.")

    # Analyse doublons
    dups = df[df.duplicated(subset=key_cols, keep=False)]
    if dups.empty:
        print("✅ Aucun doublon détecté sur les colonnes clés :", key_cols)
        continue
    print(f"⚠ {len(dups)} lignes en doublon détectées sur les clés {key_cols}.")

    grouped = dups.groupby(key_cols)
    for name, group in grouped:
        print(f"\n🔎 Doublons pour la clé {name} :")
        diff_cols = []
        for col in df.columns:
            if col in key_cols:
                continue
            if group[col].nunique(dropna=False) > 1:
                diff_cols.append(col)
        if diff_cols:
            print(f"Colonnes avec différences : {diff_cols}")
            print(group[key_cols + diff_cols])
        else:
            print("Pas de différences dans les autres colonnes.")

    # Nettoyage : garder la première occurrence
    before = len(df)
    df_clean = df.drop_duplicates(subset=key_cols, keep='first')
    after = len(df_clean)
    print(f"\n🧹 Nettoyage : {before - after} doublons supprimés, {after} lignes restantes.")

    # Sauvegarde fichier nettoyé
    out_path = os.path.join(base_dir, filename.replace(".csv.gz", "_cleaned.csv.gz"))
    df_clean.to_csv(out_path, index=False, compression='gzip')
    print(f"💾 Fichier nettoyé sauvegardé : {out_path}")
