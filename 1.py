import requests
import pandas as pd

def get_meteo_power(lat, lon, start_year=2020, end_year=2023):
    url = f"https://power.larc.nasa.gov/api/v1/data?lat={lat}&lon={lon}&start={start_year}&end={end_year}&parameters=T2M,PRECTOT,ALLSKY_SFC_SW_DWN&community=AG&format=JSON"

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erreur HTTP {response.status_code}")
        print("Contenu reçu :", response.text)
        raise Exception("Échec de la requête NASA POWER")

    try:
        data = response.json()["properties"]["parameter"]
    except Exception as e:
        print("Erreur JSON :", e)
        print("Texte brut :", response.text)
        raise

    df = pd.DataFrame({
        "year": list(data["T2M"].keys()),
        "temperature_avg_C": list(data["T2M"].values()),
        "precipitation_mm": list(data["PRECTOT"].values()),
        "solar_radiation_MJ_m2": list(data["ALLSKY_SFC_SW_DWN"].values())
    })

    return df

# Exemple d'utilisation
lat = 14.5
lon = -3.5
df_meteo = get_meteo_power(lat, lon)
df_meteo.to_csv("weather_sahel_2020_2023.csv", index=False)
print(df_meteo)
