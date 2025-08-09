import pandas as pd

# Chargement du fichier (adapter le chemin et nom fichier)
file_path = r"C:\plateforme-agricole-complete-v2\SmartSènè\Fichier pour l'entrainement de xgboost\fusion_finale.csv.gz"
print(f"📥 Chargement du fichier : {file_path}")
df = pd.read_csv(file_path, compression='gzip')

# Colonnes clés pour identifier doublons (à adapter selon tes données)
key_cols = ['country', 'year']

print(f"\n🔍 Analyse des doublons sur les colonnes clés : {key_cols}")

# Trouver les clés en doublon
dups = df[df.duplicated(subset=key_cols, keep=False)]

if dups.empty:
    print("✅ Aucun doublon trouvé sur ces colonnes clés.")
else:
    print(f"⚠ {len(dups)} lignes en doublon détectées.")

    # Pour comprendre si doublons ont valeurs différentes ailleurs, on compare ligne par ligne
    grouped = dups.groupby(key_cols)

    for name, group in grouped:
        print(f"\n🔎 Doublons pour la clé {name} :")
        # Afficher les colonnes où il y a au moins une valeur différente dans ce groupe
        diff_cols = []
        for col in df.columns:
            # ignorer colonnes clés
            if col in key_cols:
                continue
            # si plusieurs valeurs uniques dans ce groupe => diff dans la colonne
            if group[col].nunique(dropna=False) > 1:
                diff_cols.append(col)
        if diff_cols:
            print(f"Colonnes avec valeurs différentes : {diff_cols}")
            print(group[diff_cols + key_cols])
        else:
            print("Toutes les colonnes ont les mêmes valeurs pour ces doublons.")

    # Proposition nettoyage : garder la première ligne pour chaque clé
    print("\n🧹 Nettoyage : suppression des doublons (garder la première occurrence)...")
    before = len(df)
    df_clean = df.drop_duplicates(subset=key_cols, keep='first')
    after = len(df_clean)
    print(f"📉 Lignes avant nettoyage : {before}")
    print(f"📈 Lignes après nettoyage : {after}")
    print(f"📊 {before - after} doublons supprimés.")

    # Sauvegarder le fichier nettoyé (optionnel)
    output_path = file_path.replace('.csv.gz', '_cleaned.csv.gz')
    df_clean.to_csv(output_path, index=False, compression='gzip')
    print(f"\n💾 Fichier nettoyé sauvegardé sous : {output_path}")
