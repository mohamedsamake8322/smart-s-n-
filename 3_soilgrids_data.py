import requests
import pandas as pd

def get_soil(lat=12.65, lon=-8.0):
    url = f"https://rest.soilgrids.org/query?lon={lon}&lat={lat}"
    r = requests.get(url).json()
    def extract(layer, depth="0-5cm"):
        return r["properties"]["layers"][layer]["depths"][depth]["values"]["mean"]
    soil_data = {
        "pH_H2O": extract("phh2o"),
        "CEC": extract("cec"),
        "Nitrogen": extract("nitrogen"),
        "Organic_Carbon": extract("ocd"),
        "Phosphorus": extract("phosphorus")
    }
    df = pd.DataFrame([soil_data])
    df.to_csv("soil_data.csv", index=False)
    print("✅ Données de sol sauvegardées")

get_soil()
