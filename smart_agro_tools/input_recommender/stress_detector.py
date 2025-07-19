def detect_stress_from_ndvi(ndvi_profile):
    """
    Analyse une série NDVI pour détecter le stress végétatif.

    Args:
        ndvi_profile (list or np.array): série temporelle NDVI.

    Returns:
        float: facteur de stress entre 0.5 (très stressé) et 1.5 (très sain)
    """
    if not ndvi_profile or len(ndvi_profile) == 0:
        return 1.0  # profil inconnu = neutre

    avg_ndvi = sum(ndvi_profile) / len(ndvi_profile)
    if avg_ndvi < 0.3:
        return 0.6
    elif avg_ndvi < 0.5:
        return 0.9
    else:
        return 1.2
