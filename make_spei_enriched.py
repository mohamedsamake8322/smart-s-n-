# make_spei_enriched.py
import os
import pandas as pd

data_path = "C:/plateforme-agricole-complete-v2/data"
spei_file = os.path.join(data_path, "SPEI_Mali_ADM2_20250821_1546.csv")
modis_file = os.path.join(data_path, "MODIS_VI_Mali_2020_2025_mali_20250821_1503.csv")
wapor_file = os.path.join(data_path, "WAPOR_fusion_long_clean_clean.csv")  # optionnel

out_file = os.path.join(data_path, "spei_enriched_with_adm2name.csv")

def safe_read(path):
    try:
        df = pd.read_csv(path)
        print(f"[OK] lu : {os.path.basename(path)} -> {len(df)} lignes, {len(df.columns)} colonnes")
        # normaliser noms colonnes
        df.columns = df.columns.str.strip().str.lower()
        return df
    except FileNotFoundError:
        print(f"[MISSING] {os.path.basename(path)} non trouvé.")
        return pd.DataFrame()
    except Exception as e:
        print(f"[ERROR] lecture {os.path.basename(path)} : {e}")
        return pd.DataFrame()

spei = safe_read(spei_file)
modis = safe_read(modis_file)
wapor = safe_read(wapor_file)

# Si spei vide -> abort
if spei.empty:
    print("SPEI introuvable ou vide — arrêt.")
    raise SystemExit(1)

# Si adm2_name déjà présent, on sauvegarde une copie propre et on sort
if "adm2_name" in spei.columns and spei["adm2_name"].notna().any():
    print("adm2_name déjà présent dans SPEI — création d'une copie nettoyée.")
    spei.to_csv(out_file, index=False)
    print(f"[SAVED] {out_file}")
    raise SystemExit(0)

# On cherche un mapping adm2_id -> adm2_name depuis MODIS ou WAPOR
mapping = None
for df, name in ((modis, "MODIS"), (wapor, "WAPOR")):
    if not df.empty and {"adm2_id", "adm2_name"}.issubset(df.columns):
        mapping = df[["adm2_id", "adm2_name"]].dropna().drop_duplicates().set_index("adm2_id")["adm2_name"]
        print(f"[MAPPING] trouvé mapping dans {name}, {len(mapping)} paires id->name")
        break

# Si mapping absent, tenter construire mapping depuis colonnes alternatives (quelques soil files utilisent ph_adm2_name etc.)
if mapping is None:
    # chercher dans soil ou autres fichiers dans dossier data qui contiennent "adm2_name"
    for fname in os.listdir(data_path):
        if not fname.lower().endswith(".csv"):
            continue
        p = os.path.join(data_path, fname)
        try:
            df = pd.read_csv(p)
            df.columns = df.columns.str.strip().str.lower()
            if {"adm2_id", "adm2_name"}.issubset(df.columns):
                mapping = df[["adm2_id", "adm2_name"]].dropna().drop_duplicates().set_index("adm2_id")["adm2_name"]
                print(f"[MAPPING] trouvé mapping dans {fname}, {len(mapping)} paires id->name")
                break
        except Exception:
            continue

if mapping is None:
    print("Aucun mapping adm2_id->adm2_name trouvé dans MODIS/WAPOR/CSV du dossier. On va utiliser adm2_id comme nom (fallback).")
    spei["adm2_name"] = spei["adm2_id"].astype(str)
else:
    # mapper — ATTENTION aux types : forcer str pour index et clefs si besoin
    try:
        # normaliser types
        mapping.index = mapping.index.astype(str)
        spei["adm2_name"] = spei["adm2_id"].astype(str).map(mapping)
        # pour les ids non trouvés, garder la valeur id en texte (transparent)
        missing = spei["adm2_name"].isna().sum()
        if missing > 0:
            print(f"[INFO] {missing} lignes n'ont pas trouvé de nom; on mettra l'id en fallback pour ces lignes.")
            spei.loc[spei["adm2_name"].isna(), "adm2_name"] = spei.loc[spei["adm2_name"].isna(), "adm2_id"].astype(str)
    except Exception as e:
        print(f"[ERROR] mapping échoué : {e}")
        print("Fallback -> utiliser adm2_id comme adm2_name.")
        spei["adm2_name"] = spei["adm2_id"].astype(str)

# Nettoyage optionnel : trim espaces
spei["adm2_name"] = spei["adm2_name"].astype(str).str.strip()

# Sauvegarde
spei.to_csv(out_file, index=False)
print(f"[SAVED] {out_file} ({len(spei)} lignes).")
print("Terminé.")
