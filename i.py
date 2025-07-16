import pandas as pd

df = pd.read_csv(r"C:\plateforme-agricole-complete-v2\soil_profile_africa_with_country.csv")

# 🧠 Aperçu des colonnes
print("🔎 Colonnes disponibles :", df.columns.tolist())

# 🌍 Distribution par pays
print("\n📊 Points par pays :")
print(df['Country'].value_counts())

# 📦 Aperçu géographique
print("\n🌐 Coordonnées min/max :")
print(f"Longitude : {df['Longitude'].min():.2f} → {df['Longitude'].max():.2f}")
print(f"Latitude  : {df['Latitude'].min():.2f} → {df['Latitude'].max():.2f}")
