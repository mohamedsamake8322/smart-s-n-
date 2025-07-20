from smart_agro_tools.dataset_loader import load_ard

def is_sentinel_available(lat, lon, year):
    """
    Vérifie la disponibilité des images Sentinel pour une zone donnée.

    Args:
        lat (float): latitude du point.
        lon (float): longitude du point.
        year (int): année cible.

    Returns:
        bool: True si au moins une image Sentinel est disponible, False sinon.
    """
    try:
        ds = load_ard(lat, lon, year, mission="s2")
        return ds is not None and ds.time.size > 0
    except Exception:
        return False
