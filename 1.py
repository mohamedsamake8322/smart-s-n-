import requests
import pandas as pd

def get_meteo_power(lat, lon, start_year=2020, end_year=2023):
    url = "https://power.larc.nasa.gov/api/temporal/yearly/point"

    parameters = ["T2M", "PRECTOT", "ALLSKY_SFC_SW_DWN"]  # Température, pluie, radiation

    params = {
        "parameters": ",".join(parameters),
        "community": "AG",
        "longitude": lon,
        "latitude": lat,
        "start": start_year,
        "end": end_year,
        "format": "JSON"
    }

    response = requests.get(url, params=params)

    # 🛡️ Vérification du statut de réponse
    if response.status_code != 200:
        print(f"Erreur HTTP {response.status_code}")
        print("Contenu reçu :", response.text)
        raise Exception("L'API NASA POWER n'a pas répondu correctement.")

    # 🔍 Parsing du JSON sécurisé
    try:
        data = response.json()["properties"]["parameter"]
    except Exception as e:
        print("Erreur lors du parsing JSON :", e)
        print("Réponse brute :", response.text)
        raise

    # 📊 Construction du tableau
    df = pd.DataFrame({
        "year": list(data["T2M"].keys()),
        "temperature_avg_C": list(data["T2M"].values()),
        "precipitation_mm": list(data["PRECTOT"].values()),
        "solar_radiation_MJ_m2": list(data["ALLSKY_SFC_SW_DWN"].values())
    })

    return df

# 📍 Exemple d’utilisation : latitude / longitude sur le Sahel
lat = 14.5
lon = -3.5

df_meteo = get_meteo_power(lat, lon)
df_meteo.to_csv("weather_sahel_2020_2023.csv", index=False)
print(df_meteo)
