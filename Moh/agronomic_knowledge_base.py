# agronomic_knowledge_base.py

from typing import Dict, List

AGRONOMIC_PARAMETERS = {
    "soil": {
        "ph_optimal": (6.0, 7.5),
        "organic_matter": {
            "tropical": "<2%",
            "fertile": "3–6%"
        },
        "nutrients_ppm": {
            "N": "indirect (nitrate/ammonium)",
            "P": ">15 ppm (Bray I / Olsen)",
            "K": ">120 ppm"
        },
        "CEC_meq_100g": {
            "sandy": "5–10",
            "loamy": "10–20",
            "clayey": ">20"
        },
        "texture": "USDA / FAO triangle"
    },
    "crop": {
        "maize": {"N": "120–180", "P2O5": "60–90", "K2O": "60–120"},
        "rice": {"N": "80–120"},
        "growth_stages": {
            "vegetative": "N",
            "flowering": "P",
            "fruiting": "K"
        },
        "yield_target": "STCR-based",
        "planting_date": "to be cross-referenced with climate"
    },
    "environment": {
        "rainfall_mm": {
            "stress": "<500",
            "leaching": ">1000"
        },
        "temperature_C": "20–30",
        "soil_moisture": "60–80% field capacity",
        "season": {
            "dry": "slow-release solid fertilizers",
            "wet": "soluble or foliar fertilizers"
        }
    },
    "fertilizers": {
        "formulations": ["NPK 15-15-15", "DAP (18-46-0)", "Urea (46-0-0)"],
        "types": ["organic", "mineral", "soluble"],
        "pricing_source": "FAOStat or local market",
        "logistics": "region-dependent"
    },
    "ai_optimization": {
        "yield_history": True,
        "dose_vs_yield": True,
        "climate_history": "NOAA",
        "stress_index": ["NDVI", "ET₀", "Tmax"]
    },
    "micro_elements": {
        "Zn": "deficiency in alkaline soils (>7.5 pH)",
        "B": "deficiency in sandy soils",
        "S": "essential for legumes",
        "Fe": "deficiency in calcareous soils",
        "Mn": "deficiency in well-drained soils rich in OM"
    }
}

def get_crop_nutrient_needs(crop: str) -> Dict[str, str]:
    return AGRONOMIC_PARAMETERS["crop"].get(crop.lower(), {})

def get_soil_thresholds() -> Dict:
    return AGRONOMIC_PARAMETERS["soil"]

def get_environmental_guidelines() -> Dict:
    return AGRONOMIC_PARAMETERS["environment"]

def get_micro_element_notes() -> Dict[str, str]:
    return AGRONOMIC_PARAMETERS["micro_elements"]
