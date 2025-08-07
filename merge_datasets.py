import pandas as pd
import os

BASE_PATH = r"C:\plateforme-agricole-complete-v2\merged_outputs"
OUTPUT_FILE = os.path.join(BASE_PATH, "final_dataset.csv.gz")

files_available = [
    "land_water_chm.csv.gz",
    "agro_economic_context.csv.gz",
    "culture_country.csv.gz",
    "vegetation.csv.gz",
    "monthly_climate.csv.gz",
    "fixed_bio_climate.csv.gz",
    "soil_data.csv.gz",
    "yield_target.csv.gz"
]

def normalize_columns(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df

def load_csv(file, nrows=None):
    path = os.path.join(BASE_PATH, file)
    if not os.path.exists(path):
        print(f"⛔ Fichier introuvable : {file}")
        return None
    try:
        print(f"📥 Chargement : {file}")
        df = pd.read_csv(path, dtype=str, low_memory=False, nrows=nrows)
        return normalize_columns(df)
    except Exception as e:
        print(f"⛔ Erreur lecture {file} : {e}")
        return None

# 💾 Chargement des blocs
geo_files = ["yield_target.csv.gz", "land_water_chm.csv.gz", "monthly_climate.csv.gz"]
admin_files = ["soil_data.csv.gz", "fixed_bio_climate.csv.gz", "vegetation.csv.gz"]
econ_files = ["agro_economic_context.csv.gz", "culture_country.csv.gz"]

print("📍 Fusion géographique...")
df_geo = None
for f in geo_files:
    df = load_csv(f, nrows=100000)
    if df is not None and {"lon", "lat"}.issubset(df.columns):
        df_geo = df if df_geo is None else pd.merge(df_geo, df, on=["lon", "lat"], how="outer")
    else:
        print(f"⚠️ Colonnes géo absentes dans {f}")

print("📍 Fusion administrative...")
df_admin = None
admin_keys = ["adm0_name", "adm1_name", "adm2_name"]
for f in admin_files:
    df = load_csv(f)
    if df is not None and all(k in df.columns for k in admin_keys):
        df_admin = df if df_admin is None else pd.merge(df_admin, df, on=admin_keys, how="outer")
    else:
        print(f"⚠️ Clés admin absentes dans {f}")

print("📍 Fusion économique...")
df_econ = None
econ_keys = ["area", "item", "year"]
for f in econ_files:
    df = load_csv(f)
    if df is not None and all(k in df.columns for k in econ_keys):
        df_econ = df if df_econ is None else pd.merge(df_econ, df, on=econ_keys, how="outer")
    else:
        print(f"⚠️ Clés économiques absentes dans {f}")

# 🧷 Fusion finale sécurisée
df_final = df_geo if df_geo is not None else pd.DataFrame()

if df_admin is not None and all(k in df_final.columns for k in admin_keys):
    df_final = pd.merge(df_final, df_admin, how="left", on=admin_keys)
    print("✅ Fusion admin réussie")
else:
    print("⚠️ Fusion admin ignorée")

if df_econ is not None and "adm0_name" in df_final.columns:
    df_final = pd.merge(df_final, df_econ, how="left", left_on="adm0_name", right_on="area")
    print("✅ Fusion économique réussie")
else:
    print("⚠️ Fusion économique ignorée")

# 🗃️ Sauvegarde
if not df_final.empty:
    df_final.to_csv(OUTPUT_FILE, index=False, compression="gzip")
    print(f"\n✅ Dataset final sauvegardé : {OUTPUT_FILE}")
else:
    print("🚫 Aucune donnée fusionnée à sauvegarder")
