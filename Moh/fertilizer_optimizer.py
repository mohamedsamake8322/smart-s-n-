#🤖 4. Optimisation IA (LightGBM / XGBoost)
import lightgbm as lgb
import pandas as pd
import numpy as np

class FertilizerOptimizer:
    def __init__(self):
        self.model = None

    def train(self, data: pd.DataFrame):
        features = ["ph", "organic_matter", "N_ppm", "P_ppm", "K_ppm", "rainfall", "temperature"]
        target = "yield"
        self.model = lgb.LGBMRegressor()
        self.model.fit(data[features], data[target])

    def predict_yield(self, input_data: dict) -> float:
        df = pd.DataFrame([input_data])
        return self.model.predict(df)[0] if self.model else None

    def optimize_doses(self, soil: SoilData, climate: dict, base_doses: dict) -> dict:
        best_yield = 0
        best_combo = base_doses.copy()

        for delta in [-0.1, 0, 0.1]:
            test_doses = {
                "N_ppm": soil.nitrogen_ppm + base_doses["N"] * delta,
                "P_ppm": soil.phosphorus_ppm + base_doses["P"] * delta,
                "K_ppm": soil.potassium_ppm + base_doses["K"] * delta
            }
            input_data = {
                "ph": soil.ph,
                "organic_matter": soil.organic_matter,
                **test_doses,
                **climate
            }
            predicted = self.predict_yield(input_data)
            if predicted > best_yield:
                best_yield = predicted
                best_combo = test_doses

        return best_combo
