import os
from soilgrids import SoilGrids

sg = SoilGrids()

# Propriétés et profondeurs à récupérer
properties = ["soc", "phh2o", "cec", "clay", "sand"]
depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]

# Coordonnées Afrique en LAEA
west, south, east, north = -1784000, 1356000, -1140000, 1863000
crs_code = "urn:ogc:def:crs:EPSG::152160"

# Boucle principale
for prop in properties:
    folder_path = f"soilgrids_africa/{prop}"
    os.makedirs(folder_path, exist_ok=True)

    for depth in depths:
        cov_id = f"{prop}_{depth}_mean"
        output_file = os.path.join(folder_path, f"{cov_id}.tif")
        print(f"🔄 Téléchargement : {cov_id}")
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
            print(f"✅ Fichier enregistré : {output_file}")
        except Exception as e:
            print(f"⚠️ Échec pour {cov_id} → {e}")
