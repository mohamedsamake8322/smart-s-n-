import pandas as pd

# 📂 Chemin du dossier
folder = "C:/plateforme-agricole-complete-v2/Boua"

# 📁 Charger les deux fichiers
df1 = pd.read_csv(f"{folder}/weather_afrique_restruc.csv")
df2 = pd.read_csv(f"{folder}/weather_afrique_restruc1.csv")

# 🔁 Fusionner en un seul DataFrame
df_all = pd.concat([df1, df2], ignore_index=True)

# 🚿 (Optionnel) Supprimer doublons exacts
df_all.drop_duplicates(inplace=True)

# 💾 Sauvegarder le fichier final
df_all.to_csv(f"{folder}/weather_afrique_restruc_total.csv", index=False)
print("✅ Fusion terminée : weather_afrique_restruc_total.csv")
