# smart_fertilizer_engine.py

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# === 1. Base de connaissances agronomiques === #

AGRONOMIC_KNOWLEDGE = {
    "ph_optimal": (6.0, 7.5),
    "organic_matter_range": {
        "tropical": "<2%",
        "fertile": "3–6%"
    },
    "nutrient_thresholds_ppm": {
        "N": "indirect (NO3/NH4)",
        "P": ">15 ppm",
        "K": ">120 ppm"
    },
    "CEC_meq_100g": {
        "sandy": "5–10",
        "loamy": "10–20",
        "clayey": ">20"
    },
    "micro_elements": {
        "Zn": "carence en sols alcalins",
        "B": "carence en sols sableux",
        "S": "essentiel pour légumineuses",
        "Fe": "carence en sols calcaires",
        "Mn": "carence en sols riches en MO"
    },
    "crop_profiles": {
        "maïs": {
            "N": 150,
            "P2O5": 75,
            "K2O": 90,
            "stages": ["semis", "croissance", "floraison", "remplissage"],
            "calendar_days": [0, 30, 60, 90]
        },
        "riz": {
            "N": 100,
            "P2O5": 60,
            "K2O": 80,
            "stages": ["semis", "tallage", "montaison", "épiaison"],
            "calendar_days": [0, 25, 50, 75]
        }
    }
}

# === 2. Moteur de recommandation contextuel === #

@dataclass
class SoilData:
    ph: float
    organic_matter: float
    nitrogen_ppm: float
    phosphorus_ppm: float
    potassium_ppm: float

@dataclass
class FertilizationPhase:
    stage: str
    date: datetime
    N: float
    P: float
    K: float
    micro_elements: List[str]

def generate_fertilization_plan(
    crop: str,
    soil: SoilData,
    area_ha: float,
    planting_date: datetime,
    yield_target: float
) -> Dict:

    crop_data = AGRONOMIC_KNOWLEDGE["crop_profiles"].get(crop.lower())
    if not crop_data:
        raise ValueError(f"Culture inconnue : {crop}")

    # Ajustement des besoins selon le rendement cible
    base_N = crop_data["N"] * (yield_target / 6.0)
    base_P = crop_data["P2O5"] * (yield_target / 6.0)
    base_K = crop_data["K2O"] * (yield_target / 6.0)

    # Répartition par phase
    stages = crop_data["stages"]
    days = crop_data["calendar_days"]
    phases = []
    for i, stage in enumerate(stages):
        phase_date = planting_date + timedelta(days=days[i])
        phases.append(FertilizationPhase(
            stage=stage,
            date=phase_date,
            N=round(base_N * 0.25, 1),
            P=round(base_P * 0.25, 1),
            K=round(base_K * 0.25, 1),
            micro_elements=detect_micro_element_needs(soil)
        ))

    return {
        "crop": crop,
        "area_ha": area_ha,
        "yield_target": yield_target,
        "phases": [phase.__dict__ for phase in phases],
        "soil_quality": evaluate_soil(soil),
        "micro_elements": detect_micro_element_needs(soil)
    }

def evaluate_soil(soil: SoilData) -> str:
    if soil.ph < 5.5:
        return "Sol acide – risque de blocage du phosphore"
    elif soil.ph > 7.8:
        return "Sol alcalin – attention aux carences en zinc et fer"
    elif soil.organic_matter < 2.0:
        return "Sol pauvre en matière organique"
    else:
        return "Sol équilibré"

def detect_micro_element_needs(soil: SoilData) -> List[str]:
    needs = []
    if soil.ph > 7.5:
        needs.append("Zinc")
        needs.append("Fer")
    if soil.organic_matter < 2.0:
        needs.append("Soufre")
    if soil.potassium_ppm < 100:
        needs.append("Bore")
    return needs
# weather_client.py

import requests

def get_weather_forecast(lat: float, lon: float, api_key: str) -> dict:
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()
# iot_simulator.py

def get_sensor_data() -> dict:
    return {
        "soil_moisture": 52.3,  # %
        "soil_temperature": 24.1,  # °C
        "air_temperature": 29.7,  # °C
        "humidity": 68.2,  # %
        "rainfall_24h": 3.5  # mm
    }
