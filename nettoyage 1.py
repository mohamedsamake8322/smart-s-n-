def summarize_missing(df):
    print("\n📉 Résumé des valeurs manquantes par colonne :")
    missing = df.isna().sum()
    total = len(df)
    summary = pd.DataFrame({
        "Colonnes": missing.index,
        "Manquantes": missing.values,
        "Pourcentage": (missing.values / total * 100).round(2)
    }).sort_values(by="Pourcentage", ascending=False)
    print(summary)
