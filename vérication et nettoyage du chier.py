import pandas as pd
import os

base_path = r"C:\plateforme-agricole-complete-v2\SmartSènè"

def check_fusion():
    print("📥 Chargement du fichier fusionné...")
    df = pd.read_csv(os.path.join(base_path, "fusion_finale.csv"))
    print("📊 Dimensions du dataset fusionné :", df.shape)

    keys = ["country", "year"]
    unique_keys = df[keys].drop_duplicates()
    print(f"Nombre de couples (pays, année) uniques : {len(unique_keys)}")

    na_total = df.isna().sum()
    print("\n🔍 Nombre de valeurs manquantes par colonne :")
    print(na_total[na_total > 0].sort_values(ascending=False))

    # Exemple check clé source CHIRPS
    print("\n📥 Chargement fichier CHIRPS...")
    chirps = pd.read_csv(os.path.join(base_path, "CHIRPS_DAILY_PENTAD.csv"))
    # Harmonisation colonnes clés pour comparaison
    chirps = chirps.rename(columns={"ADM0_NAME": "country", "STR1_YEAR": "year"})
    chirps_keys = chirps[keys].drop_duplicates()

    missing_in_fusion = chirps_keys.merge(unique_keys, on=keys, how="left", indicator=True)
    missing_count = (missing_in_fusion["_merge"] == "left_only").sum()
    print(f"Clés CHIRPS absentes dans fusion : {missing_count}")

    # Ici tu peux ajouter pareil pour SMAP, FAOSTAT, GEDI etc.

    print("\n🔎 Exemple lignes avec NaN :")
    print(df[df.isna().any(axis=1)].head())

def clean_columns():
    df = pd.read_csv(os.path.join(base_path, "fusion_finale.csv"))
    cols_to_drop = [col for col in df.columns if
                    col.startswith("system:index") or
                    col.endswith("_right") or
                    col in ["geometry", ".geo", "index_right"]]

    print(f"Suppression de {len(cols_to_drop)} colonnes inutiles.")
    df_clean = df.drop(columns=cols_to_drop)

    output_path = os.path.join(base_path, "fusion_finale_clean.csv")
    df_clean.to_csv(output_path, index=False)
    print(f"✅ Nettoyage terminé. Fichier sauvegardé : {output_path}")

def validate_data():
    df = pd.read_csv(os.path.join(base_path, "fusion_finale_clean.csv"))
    print("📊 Statistiques descriptives :")
    print(df.describe())

    print("\nNombre de lignes par pays :")
    print(df["country"].value_counts())

    print("\nNombre de lignes par année :")
    print(df["year"].value_counts())

    if "rainfall" in df.columns:
        if (df["rainfall"] < 0).any():
            print("⚠️ Valeurs négatives détectées dans rainfall !")
        else:
            print("Rainfall OK : pas de valeurs négatives.")
    else:
        print("Colonne 'rainfall' non trouvée.")

def main():
    print("=== MENU ===")
    print("1 - Vérification fusion")
    print("2 - Nettoyage colonnes inutiles")
    print("3 - Validation finale")
    print("4 - Tout faire")
    choice = input("Choisis une option (1,2,3,4): ")

    if choice == "1":
        check_fusion()
    elif choice == "2":
        clean_columns()
    elif choice == "3":
        validate_data()
    elif choice == "4":
        check_fusion()
        clean_columns()
        validate_data()
    else:
        print("Option invalide.")

if __name__ == "__main__":
    main()
