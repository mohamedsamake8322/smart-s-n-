from region_profile import REGION_PROFILES

def get_region_by_country(country: str):
    for region in REGION_PROFILES:
        if country in region.countries:
            return region
    return None  # Par défaut, région non trouvée
