import requests
import os
import time

# 📁 Dossier de sortie
output_folder = "weather_data"
os.makedirs(output_folder, exist_ok=True)

# 📌 Paramètres (max 23 par requête)
parameters_group1 = [
    "T2M_RANGE", "T2M_MAX", "T2M_MIN", "ALLSKY_SFC_LW_DWN", "QV2M", "RH2M",
    "PRECTOT", "PRECTOTCORR", "IMERG_PRECTOT", "PS", "WS2M", "WS2M_MAX",
    "WS2M_MIN", "WS2M_RANGE", "WD2M", "WS10M", "WS10M_MAX", "WS10M_MIN",
    "WS10M_RANGE", "WD10M", "GWETTOP", "GWETROOT", "GWETPROF"
]

# 📅 Période
start_date = "20200101"
end_date = "20231231"

# 🌍 Exemple de point (latitude, longitude)
point = (10.1, -12.17)  # Mali

# 📄 Construction de l’URL
def build_power_url(lat, lon, params, start, end):
    param_str = ",".join(params)
    return (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters={param_str}&community=AG&longitude={lon}&latitude={lat}"
        f"&start={start}&end={end}&format=CSV"
    )

# 📡 Requête
def get_power_data(lat, lon, params, start, end, country_code):
    url = build_power_url(lat, lon, params, start, end)
    print(f"Requesting: {url}")

    response = requests.get(url)
    if response.status_code == 200:
        filename = f"{country_code}_{lat}_{lon}.csv"
        filepath = os.path.join(output_folder, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"✅ Saved: {filepath}")
    else:
        print(f"❌ Failed ({response.status_code}) for {lat}, {lon}")

# ▶️ Appel pour un point
get_power_data(
    lat=point[0],
    lon=point[1],
    params=parameters_group1,
    start=start_date,
    end=end_date,
    country_code="ML"
)

# 💤 Pour boucler sur plusieurs points : ajouter un délai (ex: time.sleep(2))
