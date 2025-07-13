import numpy as np

# 📦 Bounding boxes pour quelques pays africains (à compléter)
bounding_boxes = {
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
    # ➕ Tu peux ajouter les autres pays ici
}

# 📐 Espacement de la grille (en degrés)
lat_step = 2.0
lon_step = 2.0

# 📂 Résultat : dictionnaire {pays: [(lat, lon), ...]}
grilles_par_pays = {}

for code, (nom, [lon_min, lat_min, lon_max, lat_max]) in bounding_boxes.items():
    latitudes = np.arange(lat_min, lat_max + lat_step, lat_step)
    longitudes = np.arange(lon_min, lon_max + lon_step, lon_step)
    points = [(round(lat, 2), round(lon, 2)) for lat in latitudes for lon in longitudes]
    grilles_par_pays[nom] = points

# 🖨️ Exemple d'affichage
for pays, points in grilles_par_pays.items():
    print(f"{pays} → {len(points)} points")
    print(points[:5])  # aperçu
