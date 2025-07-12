import os
from soilgrids import SoilGrids

# Initialisation du client SoilGrids
sg = SoilGrids()

# Coordonnées couvrant toute l’Afrique en LAEA (EPSG:152160)
west, south, east, north = -1784000, 1356000, -1140000, 1863000
crs_code = "urn:ogc:def:crs:EPSG::152160"

# Dossiers racine
base_folder = "soilgrids_africa"

# Propriétés standards par profondeur
properties_standard = [
    "soc", "cec", "phh2o", "clay", "silt", "sand",
    "bdod", "cfvo", "nitrogen", "ocd"
]

depths = [
    "0-5cm", "5-15cm", "15-30cm",
    "30-60cm", "60-100cm", "100-200cm"
]

# Propriété spéciale : Organic Carbon Stock (ocs) → seulement sur 0-30cm
ocs_coverage_ids = ["ocs_0-30cm_Q0.05", "ocs_0-30cm_Q0.5", "ocs_0-30cm_Q0.95", "ocs_0-30cm_mean", "ocs_0-30cm_uncertainty"]

# Boucle principale – propriétés standards
for prop in properties_standard:
    folder_path = os.path.join(base_folder, prop)
    os.makedirs(folder_path, exist_ok=True)

    for depth in depths:
        cov_id = f"{prop}_{depth}_mean"
        output_file = os.path.join(folder_path, f"{cov_id}.tif")

        if os.path.exists(output_file):
            print(f"🟡 Déjà présent : {output_file}")
            continue

        try:
            sg.get_coverage_data(
                service_id=prop,
                coverage_id=cov_id,
                west=west,
                south=south,
                east=east,
                north=north,
                crs=crs_code,
                output=output_file
            )
            print(f"✅ Téléchargé : {output_file}")
        except Exception as e:
            print(f"⚠️ Échec pour {cov_id} → {e}")

# Propriété spéciale : Organic Carbon Stock (ocs)
prop = "ocs"
folder_path = os.path.join(base_folder, prop)
os.makedirs(folder_path, exist_ok=True)

for cov_id in ocs_coverage_ids:
    output_file = os.path.join(folder_path, f"{cov_id}.tif")

    if os.path.exists(output_file):
        print(f"🟡 Déjà présent : {output_file}")
        continue

    try:
        sg.get_coverage_data(
            service_id=prop,
            coverage_id=cov_id,
            west=west,
            south=south,
            east=east,
            north=north,
            crs=crs_code,
            output=output_file
        )
        print(f"✅ Téléchargé : {output_file}")
    except Exception as e:
        print(f"⚠️ Échec pour {cov_id} → {e}")
