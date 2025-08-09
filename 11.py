import pandas as pd
import os
import psutil

# 📁 Dossier des fichiers
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"
output_path = os.path.join(data_dir, "dataset_rendement_pandas.csv")

# 📦 Chargement des DataFrames déjà nettoyés
dataframes = {}  # ← à remplir avec tes fichiers nettoyés comme dans ton script précédent

# 🧠 Fonction pour log mémoire
def log_memory(prefix=""):
    mem = psutil.virtual_memory()
    print(f"{prefix}💾 RAM utilisée : {mem.used / 1e9:.2f} GB / {mem.total / 1e9:.2f} GB")

# 🔗 Fusion thématique climat + production
df_base = dataframes.get("chirps")
df_climat = df_base.merge(dataframes.get("smap"), on=["ADM0_NAME", "Year"], how="outer")
df_climat_prod = df_climat.merge(dataframes.get("production"), on=["ADM0_NAME", "Year"], how="outer")
log_memory("📊 Après fusion climat + production → ")

# 🔗 Fusion latérale GEDI
if "gedi" in dataframes:
    df_climat_prod = df_climat_prod.merge(dataframes["gedi"], on="ADM0_NAME", how="left")
    print("✅ Fusion GEDI réussie")
    log_memory("📊 Après GEDI → ")

# 🔍 Préparation intelligente du fichier resources
if "resources" in dataframes:
    df_resources = dataframes["resources"]

    # 🧼 Nettoyage des colonnes dupliquées
    df_resources = df_resources.loc[:, ~df_resources.columns.duplicated()]

    # 🔹 Réduction à une ligne par pays (moyenne ou première occurrence)
    df_resources_reduced = df_resources.groupby("ADM0_NAME").mean(numeric_only=True).reset_index()

    # 🧬 Fusion latérale optimisée
    df_climat_prod = df_climat_prod.merge(df_resources_reduced, on="ADM0_NAME", how="left")
    print(f"✅ Fusion resources réussie avec {df_resources_reduced.shape[1]} colonnes")
    log_memory("📊 Après resources → ")

# 🔗 Fusion finale avec les autres fichiers thématiques
ignored_keys = ["chirps", "smap", "production", "gedi", "resources"]
for key, df in dataframes.items():
    if key not in ignored_keys:
        try:
            df_climat_prod = df_climat_prod.merge(df, on=["ADM0_NAME", "Year"], how="outer")
            print(f"✅ Fusion {key} réussie")
            log_memory(f"📊 Après {key} → ")
        except Exception as e:
            print(f"❌ Erreur fusion {key} : {e}")

# 📐 Dimensions finales
print(f"📐 Dimensions du DataFrame final : {df_climat_prod.shape}")

# 💾 Sauvegarde finale
df_climat_prod.to_csv(output_path, index=False)
print(f"✅ Dataset fusionné sauvegardé : {output_path}")
