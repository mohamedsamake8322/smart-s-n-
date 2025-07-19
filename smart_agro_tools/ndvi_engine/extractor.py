from smart_agro_tools.ndvi_engine.validator import is_sentinel_available
from smart_agro_tools.ndvi_engine.config import MISSION_PRIORITY
from smart_agro_tools.ard_loader import load_ard
from smart_agro_tools.ndvi_core import calculate_indices
from smart_agro_tools.masking_utils import masking

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

    Raises:
        ValueError: si aucune donnée NDVI valable n'est trouvée.
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
