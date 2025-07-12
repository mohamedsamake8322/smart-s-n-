import requests
import pandas as pd

def get_weather(lat=12.65, lon=-8.0, start="20", end="2020"):
    url = f"https://power.larc.nasa.gov/api/temporal/annual/point?parameters=T2M,PRECTOT,RAD&community=AG&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON"
    r = requests.get(url)
    data = r.json()["properties"]["parameter"]
    df = pd.DataFrame({
        "Year": list(data["T2M"].keys()),
        "Temperature_C": list(data["T2M"].values()),
        "Precipitation_mm": list(data["PRECTOT"].values()),
        "Radiation_W/m2": list(data["RAD"].values())
    })
    df.to_csv("weather_data_nasa.csv", index=False)
    print("✅ Données météo sauvegardées")

get_weather()
