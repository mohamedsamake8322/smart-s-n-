import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 📥 Charger le fichier
df = pd.read_csv("SmartSènè/dataset_fusionne_pour_XGBoost.csv.gz", compression='gzip')
print(f"✅ Fichier chargé : {df.shape[0]} lignes, {df.shape[1]} colonnes")

# 🧹 Supprimer les lignes entièrement vides
df_clean = df.dropna(how='all')
print(f"🧹 Lignes restantes après suppression des lignes vides : {df_clean.shape[0]}")

# 📊 Statistiques descriptives
print("\n📊 Aperçu des colonnes numériques :")
print(df_clean.describe(include='number'))

# 📋 Colonnes avec valeurs manquantes
missing = df_clean.isnull().sum()
missing_cols = missing[missing > 0].sort_values(ascending=False)
print("\n🔍 Colonnes avec valeurs manquantes :")
print(missing_cols)

# 🧬 Vérification des doublons
num_duplicates = df_clean.duplicated().sum()
print(f"\n🧬 Nombre de doublons exacts : {num_duplicates}")

# 🔢 Types de données
print("\n🔢 Types de données par colonne :")
print(df_clean.dtypes)

# 🌍 Distribution des pays partenaires
if 'Partner Countries' in df_clean.columns:
    top_countries = df_clean['Partner Countries'].value_counts().head(10)
    print("\n🌍 Top 10 pays partenaires :")
    print(top_countries)

    # 📊 Visualisation
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_countries.values, y=top_countries.index, palette='viridis')
    plt.title("Top 10 pays partenaires")
    plt.xlabel("Nombre d'enregistrements")
    plt.ylabel("Pays")
    plt.tight_layout()
    plt.show()

# 📆 Distribution temporelle
if 'Year' in df_clean.columns:
    year_counts = df_clean['Year'].value_counts().sort_index()
    print("\n📆 Répartition des années :")
    print(year_counts)

    # 📊 Visualisation
    plt.figure(figsize=(10, 4))
    sns.lineplot(x=year_counts.index, y=year_counts.values, marker='o')
    plt.title("Distribution des données par année")
    plt.xlabel("Année")
    plt.ylabel("Nombre d'enregistrements")
    plt.tight_layout()
    plt.show()

# 🌾 Vérification du rendement si colonnes disponibles
if 'Production' in df_clean.columns and 'Area Harvested' in df_clean.columns:
    df_clean['Yield'] = df_clean['Production'] / df_clean['Area Harvested']
    print("\n🌾 Statistiques sur le rendement (Production / Surface récoltée) :")
    print(df_clean['Yield'].describe())

    # 📊 Visualisation
    plt.figure(figsize=(8, 4))
    df_clean['Yield'].hist(bins=50)
    plt.title("Distribution du rendement")
    plt.xlabel("Tonnes par hectare")
    plt.ylabel("Fréquence")
    plt.tight_layout()
    plt.show()
