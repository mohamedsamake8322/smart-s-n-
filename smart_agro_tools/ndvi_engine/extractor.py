import rasterio  # type: ignore
from rasterio.windows import Window  # type: ignore
import logging
import xarray as xr
from smart_agro_tools.ndvi_engine.validator import is_sentinel_available
from smart_agro_tools.ndvi_engine.config import MISSION_PRIORITY
from smart_agro_tools.ndvi_engine.dataset_loader import load_agricultural_data  # fonction existante

from smart_agro_tools.ndvi_core import calculate_indices  # type: ignore
from smart_agro_tools.masking_utils import masking  # type: ignore
from smart_agro_tools.ndvi_engine.extractor import extract_ndvi_profile
from smart_agro_tools.ndvi_engine.ndvi_core import calculate_indices
from smart_agro_tools.ndvi_engine.masking_utils import masking

def extract_ndvi_profile(dataset: xr.Dataset) -> dict:
    """
    Extrait le profil NDVI masqué à partir d'un Dataset satellite.

    Args:
        dataset (xr.Dataset): Données satellites avec les bandes nécessaires.

    Returns:
        dict: Dictionnaire contenant le NDVI masqué et les timestamps.
    """
    if dataset is None or 'time' not in dataset.dims or dataset.time.size == 0:
        raise ValueError("Le dataset est vide ou ne contient pas de dimension temporelle.")

    try:
        # Calculer le NDVI
        ndvi = calculate_indices(dataset, index='NDVI')

        # Appliquer le masque
        ndvi_masked = masking(ndvi)

        # Supprimer les dates sans valeur valide
        valid_ndvi = ndvi_masked.where(~ndvi_masked.isnull(), drop=True)

        if valid_ndvi.time.size == 0:
            raise ValueError("Aucune donnée NDVI valide après masquage.")

        return {
            "ndvi": valid_ndvi,
            "dates": valid_ndvi.time.values
        }

    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'extraction du profil NDVI : {e}")

def extract_valid_ndvi(lat, lon, year, mission_priority=MISSION_PRIORITY):
    """
    Extraction NDVI avec fallback sur différentes missions satellites.

    Args:
        lat (float): latitude du point.
        lon (float): longitude du point.
        year (int): année cible.
        mission_priority (list): liste ordonnée des missions satellites à tester.

    Returns:
        dict: {
            "ndvi": DataArray NDVI nettoyée,
            "source": mission utilisée
        }
    """
    for mission in mission_priority:
        try:
            logging.info(f"🔍 Tentative avec mission : {mission}")
            ds = load_agricultural_data(lat=lat, lon=lon, year=year, mission=mission)

            if ds is None:
                logging.warning(f"⚠️ Aucune donnée pour {mission} à l'emplacement ({lat}, {lon}) en {year}")
                continue

            if not hasattr(ds, "time") or ds.time.size == 0:
                logging.warning(f"⏳ Dataset vide ou sans dimension temporelle pour {mission}")
                continue

            ndvi = calculate_indices(ds, index='NDVI')
            ndvi_masked = masking(ndvi)

            if ndvi_masked.isnull().all():
                logging.warning(f"❌ NDVI entièrement nul après masquage pour {mission}")
                continue

            logging.info(f"✅ NDVI extrait avec succès depuis {mission}")
            return {
                "ndvi": ndvi_masked,
                "source": mission
            }

        except Exception as e:
            logging.error(f"❗Erreur lors de l'extraction avec {mission} : {e}")
            continue

    raise ValueError("🚫 Aucune donnée NDVI exploitable pour cette zone/année.")


def extract_ndvi_profile_from_tif(lat, lon, tif_path):
    """
    Extrait le profil NDVI d'un fichier GeoTIFF pour une position donnée.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        tif_path (str): Chemin du fichier NDVI GeoTIFF.

    Returns:
        list[float]: Valeurs NDVI normalisées (entre 0 et 1).
    """
    try:
        with rasterio.open(tif_path) as src:
            # Conversion des coordonnées (lon/lat) en indices (row, col)
            row, col = src.index(lon, lat)
            ndvi_value = src.read(1)[row, col]

            # Normaliser si besoin (ex. NDVI codé en int16)
            if ndvi_value > 1:
                ndvi_value = ndvi_value / 10000.0  # Hypothèse Sentinel-2 NDVI

            return [round(float(ndvi_value), 3)]
    except Exception as e:
        logging.error(f"⚠️ Erreur extraction NDVI depuis GeoTIFF : {e}")
        return None
