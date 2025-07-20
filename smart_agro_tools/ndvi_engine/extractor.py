import rasterio # type: ignore
from rasterio.windows import Window # type: ignore
from smart_agro_tools.ndvi_engine.validator import is_sentinel_available
from smart_agro_tools.ndvi_engine.config import MISSION_PRIORITY
from smart_agro_tools.ard_loader import load_ard # type: ignore
from smart_agro_tools.ndvi_core import calculate_indices # type: ignore
from smart_agro_tools.masking_utils import masking # type: ignore


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
            ds = load_ard(lat, lon, year, mission=mission)
            if ds is None or ds.time.size == 0:
                continue
            ndvi = calculate_indices(ds, index='NDVI')
            ndvi_masked = masking(ndvi)
            if ndvi_masked.isnull().all():
                continue
            return {
                "ndvi": ndvi_masked,
                "source": mission
            }
        except Exception:
            continue

    raise ValueError("Aucune donnée NDVI exploitable pour cette zone/année.")


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

            # Normaliser si besoin (par ex. NDVI en int16)
            if ndvi_value > 1:
                ndvi_value = ndvi_value / 10000.0  # Hypothèse Sentinel-2 NDVI

            return [round(float(ndvi_value), 3)]
    except Exception as e:
        print(f"⚠️ Erreur extraction NDVI : {e}")
        return None
