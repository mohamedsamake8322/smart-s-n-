import psycopg2 # type: ignore
from smart_agro_tools.ndvi_engine.dataset_loader import load_dataset
from smart_agro_tools.ndvi_engine.extractor import extract_ndvi_profile
from smart_agro_tools.ndvi_engine.validator import check as ndvi_check
from smart_agro_tools.input_recommender.climate_filter import filter_climate
from smart_agro_tools.input_recommender.stress_detector import detect_stress
from smart_agro_tools.input_recommender.soil_matcher import match_soil
from smart_agro_tools.input_recommender.recommender import suggest_npk
from smart_agro_tools.db_interface.ndvi_storage import store_ndvi_profile
import numpy as np # type: ignore
import os

CSV_PATH = r"C:\plateforme-agricole-complete-v2\data\dataset_agricole_prepared.csv"
NDVI_FOLDER = r"C:\plateforme-agricole-complete-v2\data\ndvi_rasters"

def compute_ndvi_stats(profile):
    arr = np.array(profile)
    return {
        "mean": float(np.mean(arr)),
        "max": float(np.max(arr)),
        "min": float(np.min(arr)),
        "std": float(np.std(arr)),
        "peak_index": int(np.argmax(arr)),
    }

def process_ndvi_data(conn):
    df = load_dataset(CSV_PATH)

    for idx, row in df.iterrows():
        lat, lon, year = row["latitude"], row["longitude"], row["year"]
        crop = row.get("culture", "unknown")

        # 1. Extraire le NDVI réel
        profile = extract_ndvi_profile(lat, lon, NDVI_FOLDER)

        # 2. Valider
        if not ndvi_check(profile):
            print(f"❌ NDVI invalide pour {crop} ({lat}, {lon})")
            continue

        # 3. Analyse et recommandations
        soil = match_soil(lat, lon)
        climate = filter_climate(lat, lon)
        stress = detect_stress(profile)
        recommendation = suggest_npk(profile, soil, climate, crop)

        stats = compute_ndvi_stats(profile)

        # 4. Stocker dans la base
        store_ndvi_profile(
            conn, lat, lon, profile, "Sentinel-2", year, stats
        )

        print(f"[{idx}] ✅ {crop} ({lat}, {lon}) | NDVI stats: {stats} | Rec: {recommendation}")

if __name__ == "__main__":
    conn = psycopg2.connect(
        host="localhost",
        dbname="datacube",
        user="mohamedsamake2000",
        password="70179877Moh#",  # ⚠️ Ton mot de passe
        port=5432
    )
    try:
        process_ndvi_data(conn)
    finally:
        conn.close()
