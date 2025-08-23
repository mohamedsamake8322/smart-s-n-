# 1) Diagnostic — exécute ça d'abord
# Sauvegarde sous diag_adm2_mapping.py et lance python diag_adm2_mapping.py.
import pandas as pd
import os

data_path = "C:/plateforme-agricole-complete-v2/data"
spei_f = os.path.join(data_path, "SPEI_Mali_ADM2_20250821_1546.csv")
modis_f = os.path.join(data_path, "MODIS_VI_Mali_2020_2025_mali_20250821_1503.csv")

def load_lower(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    return df

spei = load_lower(spei_f)
modis = load_lower(modis_f)

print("SPEI shape:", spei.shape)
print("MODIS shape:", modis.shape)
print("SPEI columns:", spei.columns.tolist())
print("MODIS columns:", modis.columns.tolist())

spei_ids = set(spei["adm2_id"].dropna().astype(str).unique())
modis_ids = set(modis["adm2_id"].dropna().astype(str).unique())

print("Unique adm2_id in SPEI:", len(spei_ids))
print("Unique adm2_id in MODIS:", len(modis_ids))
print("Sample SPEI ids (10):", list(spei_ids)[:10])
print("Sample MODIS ids (10):", list(modis_ids)[:10])

missing = sorted(list(spei_ids - modis_ids))
print("Number of SPEI ids missing in MODIS:", len(missing))
print("First 20 missing ids:", missing[:20])

# save missing list + counts
pd.Series(missing).to_csv(os.path.join(data_path, "missing_adm2ids_from_modis.csv"), index=False)
counts = spei["adm2_id"].astype(str).value_counts()
missing_counts = counts[counts.index.isin(missing)]
missing_counts.head(50).to_csv(os.path.join(data_path, "missing_adm2ids_counts.csv"))
print("Saved missing_adm2ids_from_modis.csv and missing_adm2ids_counts.csv")


 # 2) Script de normalisation + remapping (essaye plusieurs stratégies)

# Sauvegarde sous make_spei_enriched_normalized.py et lance python make_spei_enriched_normalized.py.
import os
import pandas as pd

data_path = "C:/plateforme-agricole-complete-v2/data"
spei_file = os.path.join(data_path, "SPEI_Mali_ADM2_20250821_1546.csv")
modis_file = os.path.join(data_path, "MODIS_VI_Mali_2020_2025_mali_20250821_1503.csv")
wapor_file = os.path.join(data_path, "WAPOR_fusion_long_clean_clean.csv")
out_file = os.path.join(data_path, "spei_enriched_with_adm2name_normalized.csv")

def safe_read(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()
    return df

spei = safe_read(spei_file)
modis = safe_read(modis_file) if os.path.exists(modis_file) else pd.DataFrame()
wapor = safe_read(wapor_file) if os.path.exists(wapor_file) else pd.DataFrame()

# quick helpers
def norm(x):
    if pd.isna(x):
        return x
    s = str(x).strip()
    # enlever préfixes fréquents (ex: 'ADM2_' ou 'adm2-') et zéros padding
    s = s.replace("adm2_", "").replace("ADM2_", "").replace("adm2-", "").strip()
    s = s.lstrip("0")
    return s

# préparer colonnes normalisées
spei["adm2_id_norm"] = spei["adm2_id"].astype(str).apply(norm)
if "adm2_id" in modis.columns:
    modis["adm2_id_norm"] = modis["adm2_id"].astype(str).apply(norm)
if "adm2_id" in wapor.columns:
    wapor["adm2_id_norm"] = wapor["adm2_id"].astype(str).apply(norm)

# construire mapping prioritairement modis, puis wapor
mapping = None
if not modis.empty and {"adm2_id_norm", "adm2_name"}.issubset(modis.columns):
    mapping = modis[["adm2_id_norm", "adm2_name"]].dropna().drop_duplicates().set_index("adm2_id_norm")["adm2_name"]
    print("[MAPPING] using MODIS mapping, pairs:", len(mapping))
elif not wapor.empty and {"adm2_id_norm", "adm2_name"}.issubset(wapor.columns):
    mapping = wapor[["adm2_id_norm", "adm2_name"]].dropna().drop_duplicates().set_index("adm2_id_norm")["adm2_name"]
    print("[MAPPING] using WAPOR mapping, pairs:", len(mapping))

if mapping is None:
    print("No mapping found in MODIS/WAPOR after normalization. Will fallback to using adm2_id text.")
    spei["adm2_name"] = spei["adm2_id"].astype(str)
else:
    # map
    spei["adm2_name"] = spei["adm2_id_norm"].map(mapping)
    missing = spei["adm2_name"].isna().sum()
    print("After normalized mapping, missing names:", missing)
    if missing > 0:
        # fallback: try direct id mapping (without normalization)
        if not modis.empty and {"adm2_id", "adm2_name"}.issubset(modis.columns):
            direct_map = modis[["adm2_id", "adm2_name"]].dropna().drop_duplicates().set_index(modis["adm2_id"].astype(str))["adm2_name"]
            spei.loc[spei["adm2_name"].isna(), "adm2_name"] = spei.loc[spei["adm2_name"].isna(), "adm2_id"].astype(str).map(direct_map)
        # if still missing, use adm2_id as text
        spei.loc[spei["adm2_name"].isna(), "adm2_name"] = spei.loc[spei["adm2_name"].isna(), "adm2_id"].astype(str)

# cleanup and save
spei["adm2_name"] = spei["adm2_name"].astype(str).str.strip()
spei.to_csv(out_file, index=False)
print("Saved:", out_file)



#


# enrich_spei_with_wapor.py
import os
import pandas as pd

data_path = "C:/plateforme-agricole-complete-v2/data"
spei_file = os.path.join(data_path, "SPEI_Mali_ADM2_20250821_1546.csv")
wapor_file = os.path.join(data_path, "WAPOR_fusion_long_clean_clean.csv")
out_file = os.path.join(data_path, "spei_enriched_with_wapor.csv")

# Fonction de lecture sécurisée
def safe_read(path):
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip().str.lower()
        print(f"[OK] lu : {os.path.basename(path)} -> {len(df)} lignes, {len(df.columns)} colonnes")
        return df
    except Exception as e:
        print(f"[ERROR] lecture {os.path.basename(path)} : {e}")
        return pd.DataFrame()

spei = safe_read(spei_file)
wapor = safe_read(wapor_file)

if spei.empty:
    raise SystemExit("[FATAL] SPEI introuvable ou vide")

# Vérifier si déjà enrichi
if "adm2_name" in spei.columns and spei["adm2_name"].notna().any():
    print("[INFO] SPEI déjà enrichi. Création d'une copie.")
    spei.to_csv(out_file, index=False)
    raise SystemExit(0)

# Construire mapping WAPOR
if {"adm2_id", "adm2_name"}.issubset(wapor.columns):
    mapping = wapor[["adm2_id", "adm2_name"]].drop_duplicates().set_index("adm2_id")["adm2_name"]
    print(f"[MAPPING] trouvé {len(mapping)} paires id->name dans WAPOR")
else:
    mapping = None
    print("[WARN] Mapping WAPOR non trouvé, fallback vers adm2_id")

# Appliquer mapping
if mapping is not None:
    spei["adm2_name"] = spei["adm2_id"].map(mapping)
    missing = spei["adm2_name"].isna().sum()
    if missing > 0:
        print(f"[INFO] {missing} lignes sans nom trouvé → fallback adm2_id")
        spei.loc[spei["adm2_name"].isna(), "adm2_name"] = spei.loc[spei["adm2_name"].isna(), "adm2_id"]
else:
    spei["adm2_name"] = spei["adm2_id"]

# Nettoyage final
spei["adm2_name"] = spei["adm2_name"].astype(str).str.strip()

# Sauvegarde
spei.to_csv(out_file, index=False)
print(f"[SAVED] {out_file} ({len(spei)} lignes).")
print("✅ Enrichissement terminé.")



#####
import pandas as pd
import os

data_path = "C:/plateforme-agricole-complete-v2/data"
spei_file = os.path.join(data_path, "SPEI_Mali_ADM2_20250821_1546.csv")
modis_file = os.path.join(data_path, "MODIS_VI_Mali_2020_2025_mali_20250821_1503.csv")

spei = pd.read_csv(spei_file)
modis = pd.read_csv(modis_file)

# Normaliser les colonnes
spei.columns = spei.columns.str.lower()
modis.columns = modis.columns.str.lower()

# Id uniques
spei_ids = spei['adm2_id'].unique()
modis_ids = modis['adm2_id'].unique()

# Créer un dataframe pour le mapping
mapping_df = pd.DataFrame({'spei_id': spei_ids})

# Tenter un mapping via les noms si disponible
if 'adm2_name' in modis.columns:
    modis_map = modis[['adm2_id', 'adm2_name']].drop_duplicates().set_index('adm2_id')['adm2_name']
    mapping_df['modis_name'] = mapping_df['spei_id'].map(modis_map)

# Pour les ids non trouvés, garder l'id comme fallback
mapping_df['modis_id'] = mapping_df['spei_id']
mapping_df['modis_name'] = mapping_df['modis_name'].fillna(mapping_df['spei_id'])

# Sauvegarde
out_file = os.path.join(data_path, "spei_to_modis_mapping.csv")
mapping_df.to_csv(out_file, index=False)
print(f"[SAVED] {out_file} ({len(mapping_df)} lignes)")
