import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np # type: ignore
import psycopg2  # type: ignore
import logging
from typing import Dict, Any
from smart_agro_tools.ndvi_engine.dataset_loader import load_agricultural_data
from smart_agro_tools.ndvi_engine.extractor import extract_ndvi_profile
from smart_agro_tools.ndvi_engine.validator import check as ndvi_check
from smart_agro_tools.input_recommender.climate_filter import filter_climate
from smart_agro_tools.input_recommender.stress_detector import detect_stress
from smart_agro_tools.input_recommender.soil_matcher import match_soil
from smart_agro_tools.input_recommender.recommender import suggest_npk
from smart_agro_tools.db_interface.ndvi_storage import store_ndvi_profile

# Configuration
CSV_PATH = r"C:\plateforme-agricole-complete-v2\data\dataset_agricole_prepared.csv"
NDVI_FOLDER = r"C:\plateforme-agricole-complete-v2\data\ndvi_rasters"

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def compute_ndvi_stats(profile: list[float]) -> Dict[str, Any]:
    """Calcule des statistiques simples sur un profil NDVI."""
    arr = np.array(profile)
    return {
        "mean": float(np.mean(arr)),
        "max": float(np.max(arr)),
        "min": float(np.min(arr)),
        "std": float(np.std(arr)),
        "peak_index": int(np.argmax(arr)),
    }

def process_ndvi_data(conn: psycopg2.extensions.connection) -> None:
    """Traite les données NDVI et les insère dans la base de données."""
    df = load_agricultural_data(CSV_PATH)

    for idx, row in df.iterrows():
        lat, lon, year = row["latitude"], row["longitude"], row["year"]
        crop = row.get("culture", "unknown")

        try:
            # 1. Extraction du NDVI
            profile = extract_ndvi_profile(lat, lon, NDVI_FOLDER)

            # 2. Validation
            if not ndvi_check(profile):
                logging.warning(f"[{idx}] ❌ NDVI invalide pour {crop} ({lat}, {lon})")
                continue

            # 3. Recommandations
            soil = match_soil(lat, lon)
            climate = filter_climate(lat, lon)
            stress = detect_stress(profile)
            recommendation = suggest_npk(profile, soil, climate, crop)
            stats = compute_ndvi_stats(profile)

            # 4. Insertion en base
            store_ndvi_profile(conn, lat, lon, profile, "Sentinel-2", year, stats)

            logging.info(f"[{idx}] ✅ {crop} ({lat}, {lon}) | NDVI stats: {stats} | NPK: {recommendation}")

        except Exception as e:
            logging.error(f"[{idx}] ❌ Erreur pour {crop} ({lat}, {lon}): {e}")

def get_database_connection() -> psycopg2.extensions.connection:
    """Établit une connexion à la base PostgreSQL."""
    return psycopg2.connect(
        host="localhost",
        dbname="datacube",
        user="mohamedsamake2000",
        password="70179877Moh#",  # 🔒 À externaliser dans une variable d’environnement pour plus de sécurité
        port=5432
    )

if __name__ == "__main__":
    try:
        with get_database_connection() as conn:
            process_ndvi_data(conn)
    except Exception as e:
        logging.critical(f"Connexion ou traitement impossible : {e}")
