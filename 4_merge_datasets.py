import pandas as pd

# Charge les fichiers
yield_df = pd.read_csv("Mali_Maize_yield.csv")
weather_df = pd.read_csv("weather_data_nasa.csv")
soil_df = pd.read_csv("soil_data.csv")

# Jointure simple par année
merged = pd.merge(yield_df, weather_df, on="Year")
# Ajoute les données de sol à toutes les lignes
for col in soil_df.columns:
    merged[col] = soil_df[col].iloc[0]

# Sauvegarde finale
merged.to_csv("merged_dataset.csv", index=False)
print("✅ Dataset combiné sauvegardé → merged_dataset.csv")
