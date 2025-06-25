# regional_context.py

from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Fertilizer:
    name: str
    type: str  # 'azoté', 'phosphaté', 'organique', etc.

@dataclass
class RegionProfile:
    name: str
    countries: List[str]
    agro_ecology: str
    crops: List[str]
    soils: List[str]
    fertilizers: List[Fertilizer]
    currency: str
    notes: str
    micro_elements: List[str]

# === PROFILS RÉGIONAUX === #
REGION_PROFILES = [
    RegionProfile(
        name="Soudano-Sahélienne",
        countries=["Mali", "Burkina Faso", "Niger", "Sénégal", "Nord Nigeria"],
        agro_ecology="Savane semi-aride avec saison pluvieuse courte",
        crops=["Mil", "Sorgho", "Niébé", "Arachide", "Sésame"],
        soils=["Ferrugineux tropicaux pauvres en MO", "Sols sableux acides"],
        fertilizers=[
            Fertilizer("NPK 15-15-15", "minéral"),
            Fertilizer("Urée", "azoté"),
            Fertilizer("Super triple phosphate", "phosphaté"),
            Fertilizer("Fiente de volaille", "organique"),
        ],
        currency="XOF",
        notes="Favoriser les apports en phosphore en début de cycle.",
        micro_elements=["Zinc", "Soufre"]
    ),
    RegionProfile(
        name="Équatoriale Humide",
        countries=["Côte d'Ivoire", "RDC", "Cameroun", "Guinée", "Congo"],
        agro_ecology="Forêt dense humide, précipitations abondantes",
        crops=["Manioc", "Banane plantain", "Riz pluvial", "Cacao", "Maïs"],
        soils=["Ferrallitiques acides", "Sols lixiviés pauvres en calcium"],
        fertilizers=[
            Fertilizer("Compost organique", "organique"),
            Fertilizer("NPK 12-24-12", "combiné"),
            Fertilizer("DAP", "starter"),
            Fertilizer("Phosphate naturel", "phosphaté"),
        ],
        currency="XOF",
        notes="Utiliser des engrais organiques à libération lente.",
        micro_elements=["Calcium", "Magnésium"]
    ),
    RegionProfile(
        name="Hautes Terres d’Afrique de l’Est",
        countries=["Éthiopie", "Rwanda", "Kenya", "Ouganda"],
        agro_ecology="Climat tropical tempéré par l’altitude",
        crops=["Maïs", "Haricot", "Blé", "Pomme de terre", "Café"],
        soils=["Andosols volcaniques riches", "Carencés en phosphore"],
        fertilizers=[
            Fertilizer("Urée", "azoté"),
            Fertilizer("DAP", "starter"),
            Fertilizer("NPK 23-10-5", "combiné"),
            Fertilizer("Compost", "organique"),
        ],
        currency="KES",
        notes="Attention à l’érosion sur terrains en pente.",
        micro_elements=["Bore", "Fer", "Cuivre"]
    ),
    RegionProfile(
        name="Zones Semi-Arides Australes",
        countries=["Zambie", "Zimbabwe", "Namibie", "Botswana"],
        agro_ecology="Pluviométrie faible et irrégulière",
        crops=["Maïs", "Soja", "Coton", "Tournesol"],
        soils=["Sols sableux légers", "Rétention d’eau faible"],
        fertilizers=[
            Fertilizer("NPK 20-10-10", "combiné"),
            Fertilizer("Urée", "azoté"),
            Fertilizer("Basal blend", "starter"),
            Fertilizer("Compost local", "organique"),
        ],
        currency="ZMW",
        notes="Renforcer la matière organique pour améliorer l’humidité du sol.",
        micro_elements=["Molybdène", "Soufre"]
    ),
    RegionProfile(
        name="Zones Sahariennes Irriguées",
        countries=["Mauritanie", "Nord Mali", "Tchad", "Égypte"],
        agro_ecology="Climat désertique, agriculture irriguée",
        crops=["Tomate", "Blé", "Oignon", "Datte", "Laitue"],
        soils=["Sols salins", "Sols alcalins avec besoins en correcteurs"],
        fertilizers=[
            Fertilizer("Engrais liquides NPK", "soluble"),
            Fertilizer("Ammonitrate", "azoté"),
            Fertilizer("Acide phosphorique", "nettoyant pH"),
            Fertilizer("Correcteurs de salinité", "spécial"),
        ],
        currency="EGP",
        notes="Privilégier l’irrigation de précision pour limiter la salinité.",
        micro_elements=["Bore", "Zinc", "Manganèse"]
    )
]

# === UTILITAIRES === #

def get_all_countries() -> List[str]:
    countries = [p for region in REGION_PROFILES for p in region.countries]
    return sorted(set(countries))

def get_region_by_country(country: str) -> Optional[RegionProfile]:
    for region in REGION_PROFILES:
        if country in region.countries:
            return region
    return None

def get_crops_by_country(country: str) -> List[str]:
    region = get_region_by_country(country)
    return region.crops if region else []

def get_fertilizers_by_country(country: str) -> List[str]:
    region = get_region_by_country(country)
    return [f.name for f in region.fertilizers] if region else []

def get_currency_by_country(country: str) -> str:
    region = get_region_by_country(country)
    return region.currency if region else "XOF"

def get_notes_by_country(country: str) -> str:
    region = get_region_by_country(country)
    return region.notes if region else ""

def get_micro_elements_by_country(country: str) -> List[str]:
    region = get_region_by_country(country)
    return region.micro_elements if region else []
