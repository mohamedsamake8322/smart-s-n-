from pathlib import Path
import geopandas as gpd # type: ignore
import requests
import json
from shapely.geometry import mapping # pyright: ignore[reportMissingModuleSource]
import time
# 🔐 Credentials
CLIENT_ID = "e4e33c23-cc62-40c4-b6e1-ef4a0bd9638f"
CLIENT_SECRET = "1VMH5xdZ6tjv06K1ayhCJ5Oo3GE8sv1j"

def get_token(client_id, client_secret):
    url = "https://services.sentinel-hub.com/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

token = get_token(CLIENT_ID, CLIENT_SECRET)

# 📜 Evalscript
evalscript = """//VERSION=3
function setup() {
  return {
    input: ["B08", "B04", "B11"],
    output: [
      { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
      { id: "ndmi", bands: 1, sampleType: "FLOAT32" }
    ]
  };
}
function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  let ndmi = (sample.B08 - sample.B11) / (sample.B08 + sample.B11);
  return {
    ndvi: [ndvi],
    ndmi: [ndmi]
  };
}
"""

# 📁 Dossiers
adm_level = "ADM0"
geo_dir = Path(r"C:\plateforme-agricole-complete-v2\geoboundaries") / adm_level
output_dir = Path(r"C:\plateforme-agricole-complete-v2\ndvi_results") / adm_level
output_dir.mkdir(parents=True, exist_ok=True)

# 🌍 Boucle sur tous les fichiers
for geojson_file in geo_dir.glob("geoBoundaries-*-ADM0.geojson"):
    iso3 = geojson_file.stem.split("-")[1]  # Extrait "BFA" depuis "geoBoundaries-BFA-ADM0.geojson"
    print(f"🔄 Traitement {iso3}")

    try:
        gdf = gpd.read_file(geojson_file).to_crs(epsg=4326)

        for idx, row in gdf.iterrows():
            geom_json = mapping(row.geometry)

            payload = {
                "input": {
                    "bounds": {
                        "geometry": geom_json,
                        "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
                    },
                    "data": [{
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": "2021-01-01T00:00:00Z",
                                "to": "2021-12-31T23:59:59Z"
                            }
                        }
                    }]
                },
                "aggregation": {
                    "timeRange": {
                        "from": "2021-01-01T00:00:00Z",
                        "to": "2021-12-31T23:59:59Z"
                    },
                    "aggregationInterval": {"of": "P1Y"},
                    "resx": 10,
                    "resy": 10,
                    "evalscript": evalscript
                },
                "calculations": {
                    "default": {
                        "statistics": {
                            "ndvi": {
                                "statistics": ["mean", "min", "max", "stDev", "percentile(25)", "percentile(75)"]
                            },
                            "ndmi": {
                                "statistics": ["mean", "min", "max", "stDev"]
                            }
                        }
                    }
                }
            }

            response = requests.post(
                "https://services.sentinel-hub.com/api/v1/statistics",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            out_path = output_dir / f"{iso3}_{adm_level}_{idx}_2021.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

            print(f"✅ {iso3} zone {idx} OK")
            time.sleep(1)

    except Exception as e:
        print(f"❌ Erreur {iso3}: {e}")
        with open("errors.txt", "a") as log:
            log.write(f"{iso3} → {e}\n")
