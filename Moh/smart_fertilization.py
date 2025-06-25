# smart_fertilization.py

from regional_context import RegionProfile
from utils.crop_database import CropDatabase

def generate_fertilization_plan(user_input: dict, region_profile: RegionProfile) -> dict:
    """
    Génère un plan de fertilisation personnalisé selon la culture, le sol et la région.
    """
    crop = user_input["crop"]
    area = user_input["area"]
    soil = user_input["soil_data"]
    selected_fertilizers = user_input["selected_fertilizers"]
    country = user_input.get("country", "Inconnu")

    # 1. Récupérer les besoins NPK de la culture
    crop_info = CropDatabase().get_crop_info(crop)
    total_npk = crop_info["total_nutrients"].copy()

    # 2. Ajuster selon les remarques régionales (ex. : carence en P)
    if "pauvre en p" in region_profile.notes.lower():
        total_npk["P"] *= 1.1
    if "pauvre en k" in region_profile.notes.lower():
        total_npk["K"] *= 1.1

    # 3. Répartir les doses par stade de croissance
    stages = crop_info["growth_stages"]
    plan = []
    for stage_name, stage_info in stages.items():
        plan.append({
            "stage": stage_name,
            "duration_days": stage_info["duration_days"],
            "N": stage_info["nutrients"]["N"],
            "P": stage_info["nutrients"]["P"],
            "K": stage_info["nutrients"]["K"],
            "fertilizers": selected_fertilizers
        })

    # 4. Estimation des coûts (à enrichir avec base de prix locale)
    fertilizer_unit_cost = 0.5  # €/kg (valeur fictive à remplacer)
    total_cost = sum([
        (stage["N"] + stage["P"] + stage["K"]) * fertilizer_unit_cost * area
        for stage in plan
    ])

    cost_estimate = {
        "total_cost_euros": total_cost,
        "cost_per_hectare": total_cost / area,
        "currency": region_profile.currency,
        "cost_breakdown": {
            "N": total_npk["N"] * fertilizer_unit_cost * area,
            "P": total_npk["P"] * fertilizer_unit_cost * area,
            "K": total_npk["K"] * fertilizer_unit_cost * area
        }
    }

    return {
        "plan": plan,
        "crop": crop,
        "area": area,
        "country": country,
        "currency": region_profile.currency,
        "region": region_profile.name,
        "notes": region_profile.notes,
        "micro_elements": region_profile.micro_elements,
        "cost_estimate": cost_estimate,
        "soil_analysis": soil
    }
