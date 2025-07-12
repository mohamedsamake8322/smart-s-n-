import requests
import pandas as pd

def get_meteo_power(lat, lon, start_year=2020, end_year=2024):
    url = "https://power.larc.nasa.gov/api/temporal/yearly/point"

    parameters = [
        "T2M",       # Température moyenne (°C)
        "PRECTOT",   # Précipitations totales (mm)
        "ALLSKY_SFC_SW_DWN"  # Radiation solaire (MJ/m²)
    ]

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
    data = response.json()["properties"]["parameter"]

    df = pd.DataFrame({
        "year": list(data["T2M"].keys()),
        "temperature": list(data["T2M"].values()),
        "precipitation": list(data["PRECTOT"].values()),
        "radiation": list(data["ALLSKY_SFC_SW_DWN"].values())
    })

    return df

# 📍 Exemple : Sahel (latitude, longitude)
lat = 14.5
lon = -3.5

df_meteo = get_meteo_power(lat, lon)
df_meteo.to_csv("weather_africa_2020_2024.csv", index=False)
print(df_meteo)
