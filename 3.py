import pandas as pd

print("📥 Chargement des fichiers...")
faostat_df = pd.read_csv("data/faostat_cultures.csv")
bioclim_df = pd.read_csv("data/bioclim.csv")
climat_df = pd.read_csv("data/climat_mensuel.csv")
soil_df = pd.read_csv("data/soil.csv")
indicateurs_df = pd.read_csv("data/indicateurs_agricoles.csv")

print("✅ Fichiers chargés.")

# 🧮 Reconstruction des rendements FAOSTAT
print("🧮 Reconstruction des rendements FAOSTAT...")
faostat_df["Yield_t_ha"] = faostat_df["Value_prod"] / faostat_df["Value_area"]
print("✅ Rendements reconstruits :", faostat_df.shape)

# 🔗 Fusion avec les indicateurs agricoles
print("🔗 Fusion avec les indicateurs agricoles...")
step1_df = faostat_df.merge(indicateurs_df, on=["Area", "Item", "Year"], how="left")
print("✅ Après ajout des indicateurs agricoles :", step1_df.shape)

# 🌍 Vérification des pays non appariés
missing_countries = set(step1_df["Area"]) - set(bioclim_df["ADM0_NAME"])
if missing_countries:
    print("🌍 Pays non appariés :", missing_countries)

# 🔗 Fusion FAOSTAT + BIOCLIM
print("🔗 Fusion FAOSTAT + BIOCLIM...")
step2_df = step1_df.merge(bioclim_df, left_on="Area", right_on="ADM0_NAME", how="left")
print("✅ Après FAOSTAT + BIOCLIM :", step2_df.shape)

# 🔗 Fusion avec climat mensuel
print("🔗 Fusion avec climat mensuel...")
step2_df = step2_df.merge(climat_df, on=["ADM0_NAME", "ADM1_NAME", "Year"], how="left")
print("✅ Après ajout climat mensuel :", step2_df.shape)

# 🧱 Agrégation des données de sol
print("📊 Agrégation des données de sol...")
soil_agg = soil_df.groupby(['ADM0_NAME', 'ADM1_NAME']).agg({
    'mean': 'mean',
    'min': 'mean',
    'max': 'mean',
    'stdDev': 'mean'
}).reset_index()
print("✅ Données de sol agrégées :", soil_agg.shape)

# 🔗 Fusion avec données de sol agrégées
print("🔗 Fusion avec données de sol agrégées...")
step3_df = step2_df.merge(soil_agg, on=['ADM0_NAME', 'ADM1_NAME'], how='left')
print("✅ Fusion finale :", step3_df.shape)

# 💾 Sauvegarde
step3_df.to_csv("output/fusion_agronomique_complete.csv", index=False)
print("📁 Fichier sauvegardé : fusion_agronomique_complete.csv")
