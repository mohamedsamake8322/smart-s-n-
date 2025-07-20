def adjust_for_soil(soil_data):
    """
    Ajuste le facteur de recommandation NPK selon l'humidité du sol.

    Args:
        soil_data (dict): Dictionnaire contenant les clés 'GWETPROF', 'GWETROOT', 'GWETTOP'.

    Returns:
        float: Facteur de correction multiplicatif entre 0.8 et 1.2.
    """

    # Valeurs par défaut si des clés manquent
    gwetprof = soil_data.get("GWETPROF", None)
    gwetroot = soil_data.get("GWETROOT", None)
    gwettop  = soil_data.get("GWETTOP", None)

    if None in (gwetprof, gwetroot, gwettop):
        raise ValueError("Les données du sol doivent contenir GWETPROF, GWETROOT et GWETTOP.")

    # Moyenne simple ou pondérée (si besoin)
    gwet_avg = (gwetprof + gwetroot + gwettop) / 3.0

    # Application de règles empiriques
    if gwet_avg < 0.2:
        factor = 0.85  # sol très sec → réduction de dose
    elif gwet_avg < 0.4:
        factor = 1.0   # sol moyennement humide → inchangé
    else:
        factor = 1.15  # sol bien humide → boost

    # Clamp final dans l’intervalle souhaité (0.8 à 1.2)
    return max(0.8, min(factor, 1.2))


# Exemple de test rapide
if __name__ == "__main__":
    sample_data = {
        "GWETPROF": 0.35,
        "GWETROOT": 0.42,
        "GWETTOP": 0.30
    }
    print(f"Soil adjustment factor: {adjust_for_soil(sample_data):.2f}")
