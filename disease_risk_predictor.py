import random
import logging

# 🚀 Logger Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DiseaseRiskPredictor:
    def __init__(self, disease_name, temperature, humidity, wind_speed, soil_type, aphid_population, crop_stage, season):
        self.disease_name = disease_name.lower()
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.soil_type = soil_type.lower()
        self.aphid_population = aphid_population
        self.crop_stage = crop_stage.lower()
        self.season = season.lower()

        # ✅ Input validation
        self.validate_inputs()

    def validate_inputs(self):
        """Ensures all values are valid before usage."""
        if not isinstance(self.temperature, (int, float)) or not (0 <= self.temperature <= 50):
            raise ValueError("🚨 Temperature must be a number between 0 and 50°C.")
        if not isinstance(self.humidity, (int, float)) or not (0 <= self.humidity <= 100):
            raise ValueError("🚨 Humidity must be a percentage between 0 and 100%.")
        if not isinstance(self.wind_speed, (int, float)) or self.wind_speed < 0:
            raise ValueError("🚨 Wind speed must be a non-negative number.")
        if not isinstance(self.aphid_population, int) or self.aphid_population < 0:
            raise ValueError("🚨 Aphid population must be a non-negative integer.")

    def get_seasonal_adjustment(self):
        """Adjusts risk based on the season."""
        season_factors = {
            "spring": 0.1,  
            "summer": 0.2,  
            "autumn": 0.15,  
            "winter": 0.05  
        }
        return season_factors.get(self.season, 0)

    def calculate_risk(self):
        """Calculates infection risk based on environmental conditions."""
        base_risk = 0.3 if self.disease_name == "fungal" else 0.2
        base_risk += random.uniform(0, 0.5)  # Realistic variability
        
        disease_factors = {
            "viral": {"temperature_range": (25, 35), "humidity_range": (50, 80), "insect": "aphid"},
            "bacterial": {"temperature_range": (18, 30), "humidity_range": (70, 100), "insect": None},
            "fungal": {"temperature_range": (10, 25), "humidity_range": (80, 100), "insect": None},
            "phytoplasma": {"temperature_range": (20, 32), "humidity_range": (60, 90), "insect": "leafhopper"},
            "insect_damage": {"temperature_range": (22, 38), "humidity_range": (40, 70), "insect": "thrips"}
        }

        if self.disease_name in disease_factors:
            factors = disease_factors[self.disease_name]

            if factors["temperature_range"][0] <= self.temperature <= factors["temperature_range"][1]:
                base_risk += 0.15
            if factors["humidity_range"][0] <= self.humidity <= factors["humidity_range"][1]:
                base_risk += 0.20
            if self.wind_speed > 20 and self.disease_name == "fungal":
                base_risk += 0.25  
            if self.soil_type == "clayey" and self.disease_name == "bacterial":
                base_risk += 0.10  
            if factors["insect"] and self.aphid_population > 500:
                base_risk += 0.30  

        base_risk += self.get_seasonal_adjustment()  
        base_risk = min(base_risk, 1)  

        logger.info(f"🔍 Estimated risk for {self.disease_name}: {base_risk:.2f}")
        return f"🔍 Estimated infection risk for {self.disease_name}: {base_risk:.2f} (0 = low, 1 = high)"

# ✅ Example usage
predictor = DiseaseRiskPredictor(
    disease_name="viral",
    temperature=28,
    humidity=65,
    wind_speed=10,
    soil_type="sandy",
    aphid_population=600,
    crop_stage="young plants",
    season="summer"
)

print(predictor.calculate_risk())
print("✅ Execution completed successfully!")
