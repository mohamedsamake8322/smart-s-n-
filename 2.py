import requests
import os
import time
import numpy as np

# 📁 Dossier de sortie
output_folder = "weather_data_africa"
os.makedirs(output_folder, exist_ok=True)

# 🌍 Grille simplifiée — à compléter avec les points générés depuis ta grille
grilles_par_pays = {
    "ML": ["Mali", [-12.17, 10.1, 4.27, 24.97]],
    "BJ": ["Benin", [0.77, 6.14, 3.8, 12.24]],
    "BF": ["Burkina Faso", [-5.47, 9.61, 2.18, 15.12]],
    "SN": ["Senegal", [-17.5, 12.3, -11.4, 16.7]],
    "CI": ["Côte d’Ivoire", [-8.6, 4.3, -2.5, 10.7]],
    "GH": ["Ghana", [-3.24, 4.71, 1.06, 11.1]],
    "GN": ["Guinea", [-15.13, 7.31, -7.83, 12.59]],
    "GM": ["Gambia", [-16.84, 13.13, -13.84, 13.88]],
    "GW": ["Guinea Bissau", [-16.68, 11.04, -13.7, 12.63]],
    "GQ": ["Equatorial Guinea", [9.31, 1.01, 11.29, 2.28]],
    "AO": ["Angola", [11.64, -17.93, 24.08, -4.44]],
    "CI": ["Ivory Coast", [-8.6, 4.34, -2.56, 10.52]],
    "CM": ["Cameroon", [8.49, 1.73, 16.01, 12.86]],
    "CD": ["Congo (Kinshasa)", [12.18, -13.26, 31.17, 5.26]],
    "CG": ["Congo (Brazzaville)", [11.09, -5.04, 18.45, 3.73]],
    "DJ": ["Djibouti", [41.66, 10.93, 43.32, 12.7]],
    "EG": ["Egypt", [24.7, 22.0, 36.87, 31.59]],
    "ET": ["Ethiopia", [32.95, 3.42, 47.79, 14.96]],
    "GA": ["Gabon", [8.8, -3.98, 14.43, 2.33]],
    "KE": ["Kenya", [33.89, -4.68, 41.86, 5.51]],
    "MA": ["Morocco", [-17.02, 21.42, -1.12, 35.76]],
    "MZ": ["Mozambique", [30.18, -26.74, 40.78, -10.32]],
    "MR": ["Mauritania", [-17.06, 14.62, -4.92, 27.4]],
    "MW": ["Malawi", [32.69, -16.8, 35.77, -9.23]],
    "MY": ["Malaysia", [100.09, 0.77, 119.18, 6.93]],
    "NA": ["Namibia", [11.73, -29.05, 25.08, -16.94]],
    "NE": ["Niger", [0.3, 11.66, 15.9, 23.47]],
    "NG": ["Nigeria", [2.69, 4.24, 14.58, 13.87]],
    "SD": ["Sudan", [21.94, 8.62, 38.41, 22.0]],
    "SS": ["South Sudan", [23.89, 3.51, 35.3, 12.25]],
    "SN": ["Senegal", [-17.63, 12.33, -11.47, 16.6]],
    "TD": ["Chad", [13.54, 7.42, 23.89, 23.41]],
    "TG": ["Togo", [-0.05, 5.93, 1.87, 11.02]],
    "TZ": ["Tanzania", [29.34, -11.72, 40.32, -0.95]],
    "UG": ["Uganda", [29.58, -1.44, 35.04, 4.25]],
    "ZA": ["South Africa", [16.34, -34.82, 32.83, -22.09]],
    "ZM": ["Zambia", [21.89, -17.96, 33.49, -8.24]],
    "ZW": ["Zimbabwe", [25.26, -22.27, 32.85, -15.51]]
    # ➕ Continue avec les autres pays
}

# 📌 Paramètres météo (6 bien tolérés par l'API)
parameters = [
    "T2M_RANGE", "T2M_MAX", "T2M_MIN",
    "ALLSKY_SFC_LW_DWN", "QV2M", "RH2M"
]

# 📅 Période
start_date = "20210101"
end_date = "20241231"

# 🧱 Fonction : construire URL API NASA POWER
def build_power_url(lat, lon, params, start, end):
    param_str = ",".join(params)
    return (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters={param_str}&community=AG&longitude={lon}&latitude={lat}"
        f"&start={start}&end={end}&format=CSV"
    )

# 📡 Fonction : télécharger un point météo
def get_power_data(lat, lon, params, start, end, country_name):
    url = build_power_url(lat, lon, params, start, end)
    response = requests.get(url)

    if response.status_code == 200:
        fname = f"{country_name}_{lat}_{lon}.csv".replace(" ", "_")
        fpath = os.path.join(output_folder, fname)
        with open(fpath, "wb") as f:
            f.write(response.content)
        print(f"✅ Saved: {fpath}")
        return True
    else:
        print(f"❌ Failed ({response.status_code}) at {lat}, {lon}")
        return False

# 🔁 Boucle sur tous les pays et points
for country, points in grilles_par_pays.items():
    print(f"\n🌍 Processing: {country} ({len(points)} points)")
    for lat, lon in points:
        success = get_power_data(lat, lon, parameters, start_date, end_date, country)
        time.sleep(2)  # 💤 Pause anti-saturation API
