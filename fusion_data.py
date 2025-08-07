import os
import pandas as pd
import dask.dataframe as dd
import psutil
import shutil

# 📁 Dossiers
DATA_DIR = r"C:\plateforme-agricole-complete-v2\SmartSènè"
OUTPUT_DIR = os.path.join(DATA_DIR, "merged_outputs")
TEMP_DIR = os.path.join(os.environ.get("TEMP", "/tmp"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 📏 Seuil pour basculer vers Dask
DASK_THRESHOLD = 100_000

# 📋 Log global
load_log = {"success": [], "missing": [], "error": []}

def check_memory():
    mem = psutil.virtual_memory()
    print(f"💾 RAM utilisée : {mem.percent}% ({mem.used // (1024**2)} MB)")

def detect_separator(file_path, sample_size=2048):
    with open(file_path, "r", encoding="utf-8") as f:
        sample = f.read(sample_size)
        if ";" in sample and sample.count(";") > sample.count(","):
            return ";"
        elif "\t" in sample and sample.count("\t") > sample.count(","):
            return "\t"
        else:
            return ","

def load_csv_or_dask(file_path, verbose=True):
    print(f"\n🔄 Chargement : {os.path.basename(file_path)}")
    if not os.path.exists(file_path):
        print(f"❌ Fichier introuvable : {file_path}")
        load_log["missing"].append(file_path)
        return None, "missing"

    sep = detect_separator(file_path)

    try:
        preview = pd.read_csv(file_path, sep=sep, nrows=500)
        estimated_rows = sum(1 for _ in open(file_path, "r", encoding="utf-8")) - 1

        if estimated_rows < DASK_THRESHOLD:
            df = pd.read_csv(file_path, sep=sep, low_memory=False)
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
            print(f"✅ Pandas : {len(df):,} lignes × {df.shape[1]} colonnes")
            load_log["success"].append(file_path)
            return df, "pandas"
        else:
            forced_dtypes = {"year": "int64", "month": "int64", "layer": "object"}
            df = dd.read_csv(file_path, sep=sep, assume_missing=True,
                             dtype=forced_dtypes, blocksize="16MB",
                             encoding="utf-8", on_bad_lines="skip")
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
            try:
                n_rows = df.shape[0].compute()
                print(f"✅ Dask : {n_rows:,} lignes × {df.shape[1]} colonnes")
            except Exception as dim_err:
                print(f"⚠️ Impossible de calculer les dimensions : {dim_err}")
            load_log["success"].append(file_path)
            return df, "dask"
    except Exception as e:
        print(f"⚠️ Erreur : {e}")
        load_log["error"].append((file_path, str(e)))
        return None, "error"

def cleanup_temp_files():
    try:
        for root, dirs, files in os.walk(TEMP_DIR):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except PermissionError:
                    continue
    except Exception as e:
        print(f"⚠️ Erreur nettoyage temporaire : {e}")

def merge_files(file_list, output_name, on=None, batch_size=2):
    dfs = []
    engines = []

    for file in file_list:
        path = os.path.join(DATA_DIR, file)
        df, engine = load_csv_or_dask(path)
        if df is not None:
            if on:
                missing_keys = [k for k in on if k not in df.columns]
                if missing_keys:
                    print(f"⚠️ Clés manquantes dans {file} : {missing_keys}")
            prefix = os.path.splitext(os.path.basename(file))[0][:20].replace(" ", "_")
            df = df.rename(columns={col: f"{prefix}_{col}" for col in df.columns if col not in (on or [])})
            dfs.append(df)
            engines.append(engine)

    if not dfs:
        print(f"❌ Aucun fichier valide pour {output_name}")
        return

    output_path = os.path.join(OUTPUT_DIR, output_name + ".csv.gz")
    check_memory()

    try:
        if "dask" in engines:
            merged = dfs[0]
            for i in range(1, len(dfs)):
                df = dfs[i]
                common_keys = [k for k in on if k in merged.columns and k in df.columns] if on else []
                if common_keys:
                    print(f"🔗 Fusion Dask sur clés : {common_keys}")
                    merged = merged.merge(df, on=common_keys, how="outer")
                else:
                    print(f"⚠️ Clés non trouvées, concaténation forcée")
                    merged = dd.concat([merged, df], axis=0, interleave_partitions=True)

            try:
                merged.to_csv(output_path, index=False, single_file=True, compression="gzip")
                print(f"✅ Fusion Dask terminée : {output_path}")
            except Exception as e:
                print(f"⚠️ Erreur export : {e}")
                fallback_dir = os.path.join(OUTPUT_DIR, output_name + "_parts")
                try:
                    merged.to_csv(fallback_dir, index=False, compression="gzip", single_file=False)
                    print(f"✅ Export multi-part terminé dans : {fallback_dir}")
                except Exception as fallback_err:
                    print(f"❌ Échec de l'export : {fallback_err}")
        else:
            merged = dfs[0]
            for i in range(1, len(dfs), batch_size):
                batch = dfs[i:i+batch_size]
                for df in batch:
                    common_keys = [k for k in on if k in merged.columns and k in df.columns] if on else []
                    if common_keys:
                        print(f"🔗 Fusion Pandas sur clés : {common_keys}")
                        merged = pd.merge(merged, df, on=common_keys, how="outer")
                    else:
                        print(f"⚠️ Clés non trouvées, concaténation forcée")
                        merged = pd.concat([merged, df], axis=0, ignore_index=True)

            merged.to_csv(output_path, index=False, compression="gzip")
            print(f"✅ Fusion Pandas terminée : {output_path}")
    except Exception as final_err:
        print(f"❌ Échec fusion/export : {final_err}")
    finally:
        cleanup_temp_files()

# 🔹 Fichiers lourds à fusionner
heavy_categories = {
    "vegetation": [
        "fusion_finale ndvi-001.csv",
        "NDMI_Afrique_fusionné.csv",
        "GEDI_Mangrove_CSV.csv"
    ],
    "soil_data": [
        "Soil_AllLayers_AllAfrica-002.csv",
        "SMAP_SoilMoisture.csv"
    ],
    "fixed_bio_climate": [
        "WorldClim BIO Variables V1.csv",
        "WAPOR_All_Variables_Merged.csv"
    ]
}

merge_keys = {
    "vegetation": ["adm0_name", "month", "year"],
    "soil_data": ["adm0_name", "layer"],
    "fixed_bio_climate": ["adm0_name", "year"]
}

for name, files in heavy_categories.items():
    keys = merge_keys.get(name)
    merge_files(files, name, on=keys)

# 📋 Export des logs
pd.DataFrame(load_log["success"], columns=["Fichiers chargés"]).to_csv(
    os.path.join(OUTPUT_DIR, "log_success.csv"), index=False
)
pd.DataFrame(load_log["missing"], columns=["Fichiers manquants"]).to_csv(
    os.path.join(OUTPUT_DIR, "log_missing.csv"), index=False
)
pd.DataFrame(load_log["error"], columns=["Fichier", "Erreur"]).to_csv(
    os.path.join(OUTPUT_DIR, "log_errors.csv"), index=False
)

print("\n📊 Résumé du traitement :")
print(f"✅ Fichiers chargés : {len(load_log['success'])}")
print(f"❌ Fichiers manquants : {len(load_log['missing'])}")
print(f"⚠️ Fichiers en erreur : {len(load_log['error'])}")
