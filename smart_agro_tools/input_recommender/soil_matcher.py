def adjust_for_soil(soil_data):
    """
    Modifie les recommandations selon les propriétés du sol.

    Args:
        soil_data (dict): contient GWETPROF, GWETROOT, GWETTOP.

    Returns:
        float: facteur multiplicatif (0.8 à 1.2)
    """
    gwet_avg = sum([soil_data.get(k, 0) for k in ['GWETPROF', 'GWETROOT', 'GWETTOP']]) / 3
    if gwet_avg < 0.2:
        return 0.85
    elif gwet_avg < 0.4:
        return 1.0
    else:
        return 1.15
