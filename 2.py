from soilgrids import SoilGrids
import os

sg = SoilGrids()
properties = ["soc", "cec", "phh2o", "clay", "silt", "sand", "bdod", "cfvo", "nitrogen", "ocs", "ocd"]
depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]

for prop in properties:
    folder = f"soilgrids_africa/{prop}"
    os.makedirs(folder, exist_ok=True)
    for depth in depths:
        cov_id = f"{prop}_{depth}_mean"
        output = f"{folder}/{cov_id}.tif"
        try:
            sg.get_coverage_data(
                service_id=prop,
                coverage_id=cov_id,
                west=-1784000, south=1356000,
                east=-1140000, north=1863000,
                crs="urn:ogc:def:crs:EPSG::152160",
                output=output
            )
            print(f"✅ {output}")
        except Exception as e:
            print(f"⚠️ Échec pour {cov_id} → {e}")
