﻿import json
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime


class DiseaseDatabase:
    """
    Base de donnÃ©es complÃ¨te des maladies agricoles
    Contient informations, symptÃ´mes, traitements et prÃ©ventions
    """

    def __init__(self):
        self.diseases_data = self._initialize_disease_database()
        self.treatments_data = self._initialize_treatments_database()
        self.prevention_data = self._initialize_prevention_database()

    def _initialize_disease_database(self) -> Dict[str, Dict]:
        """
        Initialise la base de donnÃ©es des maladies
        """
        return {
            "Tomato_Late_blight": {
                "name": "Mildiou de la Tomate",
                "scientific_name": "Phytophthora infestans",
                "category": "Fongiques",
                "cause": "OomycÃ¨te pathogÃ¨ne",
                "description": "Maladie destructrice causant des taches brunes sur feuilles, tiges et fruits",
                "severity": "Ã‰levÃ©e",
                "season": "Temps humide et frais",
                "affected_crops": ["Tomate", "Pomme de terre"],
                "symptoms": [
                    "Taches brunes irrÃ©guliÃ¨res sur les feuilles",
                    "FlÃ©trissement rapide des feuilles",
                    "Taches sombres sur les tiges",
                    "Pourriture des fruits",
                    "Duvet blanc sous les feuilles par temps humide",
                ],
                "favorable_conditions": [
                    "TempÃ©rature 15-20Â°C",
                    "HumiditÃ© Ã©levÃ©e (>85%)",
                    "Temps pluvieux",
                    "Mauvaise circulation d'air",
                ],
            },
            "Tomato_Early_blight": {
                "name": "Alternariose de la Tomate",
                "scientific_name": "Alternaria solani",
                "category": "Fongiques",
                "cause": "Champignon pathogÃ¨ne",
                "description": "Maladie fongique causant des taches concentriques caractÃ©ristiques",
                "severity": "ModÃ©rÃ©e",
                "season": "Ã‰tÃ© chaud et humide",
                "affected_crops": ["Tomate", "Pomme de terre", "Aubergine"],
                "symptoms": [
                    "Taches circulaires brunes avec anneaux concentriques",
                    "Jaunissement et flÃ©trissement des feuilles infÃ©rieures",
                    "Taches sur les tiges et pÃ©tioles",
                    "Pourriture des fruits prÃ¨s du pÃ©doncule",
                ],
                "favorable_conditions": [
                    "TempÃ©rature 24-29Â°C",
                    "Alternance humiditÃ©/sÃ©cheresse",
                    "Stress hydrique",
                    "Plants affaiblis",
                ],
            },
            "Tomato_Bacterial_spot": {
                "name": "Tache BactÃ©rienne de la Tomate",
                "scientific_name": "Xanthomonas spp.",
                "category": "BactÃ©riennes",
                "cause": "BactÃ©rie pathogÃ¨ne",
                "description": "Infection bactÃ©rienne causant des petites taches noires sur feuilles et fruits",
                "severity": "ModÃ©rÃ©e",
                "season": "Temps chaud et humide",
                "affected_crops": ["Tomate", "Poivron"],
                "symptoms": [
                    "Petites taches noires avec halo jaune",
                    "Taches sur feuilles, tiges et fruits",
                    "DÃ©foliation en cas d'infection sÃ©vÃ¨re",
                    "Fruits craquelÃ©s et dÃ©formÃ©s",
                ],
                "favorable_conditions": [
                    "TempÃ©rature 25-30Â°C",
                    "HumiditÃ© Ã©levÃ©e",
                    "Blessures sur les plants",
                    "Propagation par Ã©claboussures",
                ],
            },
            "Potato_Late_blight": {
                "name": "Mildiou de la Pomme de Terre",
                "scientific_name": "Phytophthora infestans",
                "category": "Fongiques",
                "cause": "OomycÃ¨te pathogÃ¨ne",
                "description": "Maladie la plus destructrice de la pomme de terre",
                "severity": "TrÃ¨s Ã‰levÃ©e",
                "season": "Temps frais et humide",
                "affected_crops": ["Pomme de terre", "Tomate"],
                "symptoms": [
                    "Taches brunes aqueuses sur feuilles",
                    "Pourriture noire des tubercules",
                    "FlÃ©trissement rapide du feuillage",
                    "Odeur dÃ©sagrÃ©able des tubercules infectÃ©s",
                ],
                "favorable_conditions": [
                    "TempÃ©rature 10-20Â°C",
                    "HumiditÃ© >90%",
                    "Temps pluvieux prolongÃ©",
                    "RosÃ©e persistante",
                ],
            },
            "Corn_Common_rust": {
                "name": "Rouille Commune du MaÃ¯s",
                "scientific_name": "Puccinia sorghi",
                "category": "Fongiques",
                "cause": "Champignon pathogÃ¨ne",
                "description": "Maladie fongique caractÃ©risÃ©e par des pustules orange-brun",
                "severity": "ModÃ©rÃ©e",
                "season": "Ã‰tÃ© frais et humide",
                "affected_crops": ["MaÃ¯s"],
                "symptoms": [
                    "Pustules orange-brun sur les feuilles",
                    "Pustules ovales Ã  circulaires",
                    "Jaunissement des feuilles",
                    "RÃ©duction du rendement en grains",
                ],
                "favorable_conditions": [
                    "TempÃ©rature 16-23Â°C",
                    "HumiditÃ© Ã©levÃ©e",
                    "RosÃ©e matinale",
                    "VariÃ©tÃ©s sensibles",
                ],
            },
            "Wheat_Leaf_rust": {
                "name": "Rouille Brune du BlÃ©",
                "scientific_name": "Puccinia triticina",
                "category": "Fongiques",
                "cause": "Champignon pathogÃ¨ne",
                "description": "Maladie importante du blÃ© causant des pertes de rendement",
                "severity": "Ã‰levÃ©e",
                "season": "Printemps et dÃ©but Ã©tÃ©",
                "affected_crops": ["BlÃ©", "Orge"],
                "symptoms": [
                    "Pustules orange-brun sur les feuilles",
                    "Taches circulaires Ã  ovales",
                    "Jaunissement prÃ©maturÃ©",
                    "RÃ©duction du poids des grains",
                ],
                "favorable_conditions": [
                    "TempÃ©rature 15-22Â°C",
                    "HumiditÃ© Ã©levÃ©e",
                    "Irrigation par aspersion",
                    "DensitÃ© de plantation Ã©levÃ©e",
                ],
            },
            "Rice_Blast": {
                "name": "Pyriculariose du Riz",
                "scientific_name": "Magnaporthe oryzae",
                "category": "Fongiques",
                "cause": "Champignon pathogÃ¨ne",
                "description": "Maladie la plus destructrice du riz dans le monde",
                "severity": "TrÃ¨s Ã‰levÃ©e",
                "season": "Saison des pluies",
                "affected_crops": ["Riz"],
                "symptoms": [
                    "Taches losangiques gris-brun sur feuilles",
                    "LÃ©sions sur le col de la panicule",
                    "Ã‰chaudage des grains",
                    "Cassure des tiges",
                ],
                "favorable_conditions": [
                    "TempÃ©rature 25-28Â°C",
                    "HumiditÃ© Ã©levÃ©e",
                    "Fertilisation azotÃ©e excessive",
                    "VariÃ©tÃ©s sensibles",
                ],
            },
            "Grape_Powdery_mildew": {
                "name": "OÃ¯dium de la Vigne",
                "scientific_name": "Erysiphe necator",
                "category": "Fongiques",
                "cause": "Champignon pathogÃ¨ne",
                "description": "Maladie fongique formant un duvet blanc sur les organes verts",
                "severity": "Ã‰levÃ©e",
                "season": "Printemps et Ã©tÃ©",
                "affected_crops": ["Vigne", "Raisin"],
                "symptoms": [
                    "Duvet blanc poudreux sur feuilles",
                    "Taches blanches sur les grappes",
                    "DÃ©formation des feuilles",
                    "Ã‰clatement des baies",
                ],
                "favorable_conditions": [
                    "TempÃ©rature 20-27Â°C",
                    "HumiditÃ© modÃ©rÃ©e",
                    "Temps sec aprÃ¨s rosÃ©e",
                    "Mauvaise aÃ©ration",
                ],
            },
            "Pepper_Bacterial_spot": {
                "name": "Tache BactÃ©rienne du Poivron",
                "scientific_name": "Xanthomonas campestris",
                "category": "BactÃ©riennes",
                "cause": "BactÃ©rie pathogÃ¨ne",
                "description": "Infection bactÃ©rienne affectant feuilles et fruits du poivron",
                "severity": "ModÃ©rÃ©e",
                "season": "Temps chaud et humide",
                "affected_crops": ["Poivron", "Piment", "Tomate"],
                "symptoms": [
                    "Petites taches brunes avec halo jaune",
                    "Taches liÃ©geuses sur les fruits",
                    "DÃ©foliation sÃ©vÃ¨re",
                    "RÃ©duction de la qualitÃ© des fruits",
                ],
                "favorable_conditions": [
                    "TempÃ©rature 24-30Â°C",
                    "HumiditÃ© Ã©levÃ©e",
                    "Blessures mÃ©caniques",
                    "Propagation par eau",
                ],
            },
            "Healthy": {
                "name": "Plant Saine",
                "scientific_name": "N/A",
                "category": "Aucune",
                "cause": "Aucune",
                "description": "Plant en bonne santÃ© sans signes de maladie",
                "severity": "Aucune",
                "season": "N/A",
                "affected_crops": ["Toutes"],
                "symptoms": [
                    "Feuillage vert et vigoureux",
                    "Croissance normale",
                    "Absence de taches ou lÃ©sions",
                    "SystÃ¨me racinaire sain",
                ],
                "favorable_conditions": [
                    "Nutrition Ã©quilibrÃ©e",
                    "Irrigation adÃ©quate",
                    "Bonne aÃ©ration",
                    "Conditions climatiques favorables",
                ],
            },
        }

    def _initialize_treatments_database(self) -> Dict[str, List[Dict]]:
        """
        Initialise la base de donnÃ©es des traitements
        """
        return {
            "Tomato_Late_blight": [
                {
                    "type": "Fongicide prÃ©ventif",
                    "description": "Application de fongicides cupriques avant l'apparition des symptÃ´mes",
                    "products": [
                        "Bouillie bordelaise",
                        "Oxychlorure de cuivre",
                        "MancozÃ¨be",
                    ],
                    "application": "PulvÃ©risation foliaire tous les 7-10 jours",
                    "timing": "Avant et pendant les pÃ©riodes Ã  risque",
                },
                {
                    "type": "Fongicide curatif",
                    "description": "Traitement systÃ©mique dÃ¨s les premiers symptÃ´mes",
                    "products": ["MÃ©talaxyl", "Cymoxanil", "Fluazinam"],
                    "application": "PulvÃ©risation avec adjuvant",
                    "timing": "DÃ¨s dÃ©tection des premiers symptÃ´mes",
                },
                {
                    "type": "Mesures culturales",
                    "description": "AmÃ©lioration des conditions de culture",
                    "products": [
                        "Paillis plastique",
                        "SystÃ¨me d'irrigation goutte-Ã -goutte",
                    ],
                    "application": "Installation en dÃ©but de culture",
                    "timing": "Avant plantation",
                },
            ],
            "Tomato_Early_blight": [
                {
                    "type": "Fongicide prÃ©ventif",
                    "description": "Protection avant apparition des symptÃ´mes",
                    "products": ["Chlorothalonil", "MancozÃ¨be", "Azoxystrobine"],
                    "application": "PulvÃ©risation rÃ©guliÃ¨re",
                    "timing": "DÃ¨s la formation des premiers fruits",
                },
                {
                    "type": "BiocontrÃ´le",
                    "description": "Utilisation d'agents biologiques",
                    "products": ["Bacillus subtilis", "Trichoderma harzianum"],
                    "application": "Traitement des semences et sol",
                    "timing": "Avant semis et plantation",
                },
            ],
            "Tomato_Bacterial_spot": [
                {
                    "type": "BactÃ©ricide cuivre",
                    "description": "Application de produits cupriques",
                    "products": ["Sulfate de cuivre", "Hydroxyde de cuivre"],
                    "application": "PulvÃ©risation prÃ©ventive",
                    "timing": "Conditions favorables prÃ©vues",
                },
                {
                    "type": "RÃ©sistance variÃ©tale",
                    "description": "Utilisation de variÃ©tÃ©s rÃ©sistantes",
                    "products": ["VariÃ©tÃ©s certifiÃ©es rÃ©sistantes"],
                    "application": "Choix variÃ©tal",
                    "timing": "Avant plantation",
                },
            ],
            "Corn_Common_rust": [
                {
                    "type": "Fongicide foliaire",
                    "description": "Traitement prÃ©ventif des feuilles",
                    "products": ["TÃ©buconazole", "Propiconazole", "Azoxystrobine"],
                    "application": "PulvÃ©risation aÃ©rienne ou terrestre",
                    "timing": "Avant floraison",
                }
            ],
            "Wheat_Leaf_rust": [
                {
                    "type": "Fongicide systÃ©mique",
                    "description": "Protection systÃ©mique de la plante",
                    "products": ["TÃ©buconazole", "Propiconazole", "Ã‰poxiconazole"],
                    "application": "PulvÃ©risation foliaire",
                    "timing": "Montaison Ã  Ã©piaison",
                }
            ],
            "Rice_Blast": [
                {
                    "type": "Fongicide systÃ©mique",
                    "description": "Traitement prÃ©ventif et curatif",
                    "products": ["Tricyclazole", "Carbendazime", "Isoprothiolane"],
                    "application": "PulvÃ©risation ou granulÃ©s",
                    "timing": "Stades critiques de dÃ©veloppement",
                }
            ],
            "Grape_Powdery_mildew": [
                {
                    "type": "Fongicide prÃ©ventif",
                    "description": "Protection avant infection",
                    "products": ["Soufre", "Kresoxim-mÃ©thyl", "Myclobutanil"],
                    "application": "Poudrage ou pulvÃ©risation",
                    "timing": "DÃ©bourrement Ã  vÃ©raison",
                }
            ],
            "Pepper_Bacterial_spot": [
                {
                    "type": "BactÃ©ricide prÃ©ventif",
                    "description": "Protection contre l'infection bactÃ©rienne",
                    "products": ["Streptomycine", "Kasugamycine", "Cuivre"],
                    "application": "PulvÃ©risation prÃ©ventive",
                    "timing": "Conditions favorables",
                }
            ],
        }

    def _initialize_prevention_database(self) -> Dict[str, List[str]]:
        """
        Initialise la base de donnÃ©es des mesures prÃ©ventives
        """
        return {
            "Tomato_Late_blight": [
                "Ã‰viter l'irrigation par aspersion",
                "Assurer une bonne aÃ©ration entre les plants",
                "Ã‰liminer les rÃ©sidus de culture infectÃ©s",
                "Rotation des cultures (3-4 ans)",
                "Utiliser des semences certifiÃ©es",
                "Drainage efficace des parcelles",
                "Ã‰viter l'excÃ¨s d'azote",
                "Surveillance mÃ©tÃ©orologique",
            ],
            "Tomato_Early_blight": [
                "Rotation des cultures",
                "Ã‰limination des dÃ©bris vÃ©gÃ©taux",
                "Irrigation au pied des plants",
                "Ã‰viter le stress hydrique",
                "Fertilisation Ã©quilibrÃ©e",
                "Espacement adÃ©quat des plants",
                "Utilisation de paillis",
                "VariÃ©tÃ©s rÃ©sistantes",
            ],
            "Tomato_Bacterial_spot": [
                "Semences traitÃ©es et certifiÃ©es",
                "DÃ©sinfection des outils",
                "Ã‰viter la manipulation par temps humide",
                "ContrÃ´le des insectes vecteurs",
                "Irrigation localisÃ©e",
                "Ã‰limination des plants infectÃ©s",
                "Rotation avec cultures non-hÃ´tes",
                "HygiÃ¨ne stricte en serre",
            ],
            "Corn_Common_rust": [
                "Utilisation de variÃ©tÃ©s rÃ©sistantes",
                "Rotation des cultures",
                "Ã‰limination des rÃ©sidus infectÃ©s",
                "Ã‰viter les semis tardifs",
                "Fertilisation azotÃ©e modÃ©rÃ©e",
                "Surveillance rÃ©guliÃ¨re",
                "Espacement optimal des plants",
            ],
            "Wheat_Leaf_rust": [
                "VariÃ©tÃ©s rÃ©sistantes ou tolÃ©rantes",
                "Rotation des cultures",
                "Ã‰limination des repousses",
                "Semis Ã  la date optimale",
                "Fertilisation Ã©quilibrÃ©e",
                "Surveillance des bulletins d'alerte",
                "Ã‰viter les densitÃ©s excessives",
            ],
            "Rice_Blast": [
                "VariÃ©tÃ©s rÃ©sistantes",
                "Gestion de l'eau d'irrigation",
                "Fertilisation azotÃ©e raisonnÃ©e",
                "Ã‰limination des chaumes infectÃ©s",
                "Rotation avec cultures sÃ¨ches",
                "Semences saines",
                "Ã‰viter l'excÃ¨s d'humiditÃ©",
            ],
            "Grape_Powdery_mildew": [
                "Taille pour aÃ©rer la vÃ©gÃ©tation",
                "Ã‰limination des sarments infectÃ©s",
                "Palissage pour Ã©viter l'ombrage",
                "Ã‰viter l'excÃ¨s d'azote",
                "VariÃ©tÃ©s moins sensibles",
                "Surveillance mÃ©tÃ©orologique",
                "Nettoyage d'hiver rigoureux",
            ],
            "Pepper_Bacterial_spot": [
                "Semences certifiÃ©es",
                "Rotation avec cultures non-solanacÃ©es",
                "Ã‰viter l'irrigation par aspersion",
                "DÃ©sinfection des outils et structures",
                "Ã‰limination des plants infectÃ©s",
                "ContrÃ´le de l'humiditÃ© en serre",
                "Ã‰viter les blessures mÃ©caniques",
            ],
        }

    def get_disease_info(self, disease_name: str) -> Optional[Dict]:
        """
        RÃ©cupÃ¨re les informations complÃ¨tes d'une maladie
        """
        return self.diseases_data.get(
            disease_name, None
        )  # Assure un retour explicite si la maladie n'existe pas

    def get_treatment_info(self, disease_name: str) -> List[Dict]:
        """
        RÃ©cupÃ¨re les informations de traitement d'une maladie
        """
        return self.treatments_data.get(disease_name, [])

    def get_prevention_info(self, disease_name: str) -> List[str]:
        """
        RÃ©cupÃ¨re les mesures prÃ©ventives d'une maladie
        """
        return self.prevention_data.get(disease_name, [])

    def get_all_diseases(self) -> List[Dict]:
        """
        RÃ©cupÃ¨re la liste de toutes les maladies
        """
        diseases = []
        return list(
            self.diseases_data.values()
        )  # Retourne directement toutes les maladies sans manipulation inutile

    def search_diseases(self, query: str, category: str = None) -> List[Dict]:
        """
        Recherche des maladies par nom ou symptÃ´me
        """
        query_lower = query.lower()
        results = []

        for disease_id, disease_data in self.diseases_data.items():
            # Search in name, scientific name, and symptoms
            searchable_text = (
                disease_data.get("name", "").lower()
                + " "
                + disease_data.get("scientific_name", "").lower()
                + " "
                + " ".join(disease_data.get("symptoms", [])).lower()
            )

            if query_lower in searchable_text:
                if category is None or disease_data.get("category") == category:
                    disease_info = disease_data.copy()
                    disease_info["id"] = disease_id
                    results.append(disease_info)

        return results

    def get_diseases_by_crop(self, crop_name: str) -> List[Dict]:
        """
        RÃ©cupÃ¨re les maladies affectant une culture spÃ©cifique
        """
        crop_diseases = []

        for disease_id, disease_data in self.diseases_data.items():
            affected_crops = disease_data.get("affected_crops", [])

            for crop in affected_crops:
                if crop_name.lower() in crop.lower():
                    disease_info = disease_data.copy()
                    disease_info["id"] = disease_id
                    crop_diseases.append(disease_info)
                    break

        return crop_diseases

    def get_disease_statistics(self) -> Dict[str, Any]:
        """
        GÃ©nÃ¨re des statistiques sur la base de donnÃ©es des maladies
        """
        total_diseases = len(self.diseases_data)

        # Count by category
        category_counts = {}
        severity_counts = {}
        crop_counts = {}

        for disease_data in self.diseases_data.values():
            # Category stats
            category = disease_data.get("category", "Unknown")
            category_counts[category] = category_counts.get(category, 0) + 1

            # Severity stats
            severity = disease_data.get("severity", "Unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            # Crop stats
            for crop in disease_data.get("affected_crops", []):
                crop_counts[crop] = crop_counts.get(crop, 0) + 1

        return {
            "total_diseases": total_diseases,
            "category_distribution": category_counts,
            "severity_distribution": severity_counts,
            "most_affected_crops": dict(
                sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "database_version": datetime.now().strftime("%Y-%m-%d"),
            "coverage": {
                "fungal_diseases": category_counts.get("Fongiques", 0),
                "bacterial_diseases": category_counts.get("BactÃ©riennes", 0),
                "viral_diseases": category_counts.get("Virales", 0),
                "parasitic_diseases": category_counts.get("Parasitaires", 0),
            },
        }


def export_database(self, format_type: str = "json") -> str:
    """
    Exporte la base de donnÃ©es au format spÃ©cifiÃ©.
    """
    if not self.diseases_data:
        raise ValueError("ðŸš¨ La base de donnÃ©es est vide, impossible d'exporter.")

    if format_type == "json":
        export_data = {
            "diseases": self.diseases_data,
            "treatments": self.treatments_data,
            "prevention": self.prevention_data,
            "export_date": datetime.now().isoformat(),
            "version": "1.0",
        }
        return json.dumps(export_data, ensure_ascii=False, indent=2)

    elif format_type == "csv":
        # Convertir en DataFrame pour l'export CSV
        diseases_list = []
        for disease_id, disease_data in self.diseases_data.items():
            row = disease_data.copy()
            row["disease_id"] = disease_id
            row["symptoms"] = "; ".join(row.get("symptoms", []))
            row["affected_crops"] = "; ".join(row.get("affected_crops", []))
            row["favorable_conditions"] = "; ".join(row.get("favorable_conditions", []))
            diseases_list.append(row)

        df = pd.DataFrame(diseases_list)
        return df.to_csv(index=False)

    else:
        raise ValueError(f"ðŸš¨ Format non supportÃ©: {format_type}")

    def add_disease(self, disease_id: str, disease_data: Dict) -> bool:
        """
        Ajoute une nouvelle maladie Ã  la base de donnÃ©es
        """
        try:
            if disease_id not in self.diseases_data:
                self.diseases_data[disease_id] = disease_data
                return True
            else:
                return False  # Disease already exists
        except Exception as e:
            print(f"Erreur lors de l'ajout de la maladie: {e}")
            return False

    def update_disease(self, disease_id: str, updated_data: Dict) -> bool:
        """
        Met Ã  jour les informations d'une maladie existante
        """
        try:
            if disease_id in self.diseases_data:
                self.diseases_data[disease_id].update(updated_data)
                return True
            else:
                return False  # Disease not found
        except Exception as e:
            print(f"Erreur lors de la mise Ã  jour de la maladie: {e}")
            return False

