import os
import requests
import json
import geopandas as gpd
from shapely.geometry import mapping
# ────────────────────── 🔐 CREDENTIALS ──────────────────────
CLIENT_ID = "7e9fed76-ac65-4c22-af08-1cca357dd856"
CLIENT_SECRET = "1t2H088gQGi7AUqJc2mcpL3gS9xhW17V"

# ────────────────────── 📍 LOAD GEOMETRY ──────────────────────
gdf = gpd.read_file(r"C:\plateforme-agricole-complete-v2\gadm\BFA\level1.geojson")
geom_json = mapping(gdf.geometry[0])

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
print("Token OK")

print("✅ Token OK")

# ────────────────────── 📜 EVALSCRIPT ──────────────────────
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

# ────────────────────── 📦 LOOP OVER FILES ──────────────────────
from pathlib import Path

GEO_ROOT = Path(r"C:\plateforme-agricole-complete-v2\geoboundaries")

for level in ["ADM0", "ADM1", "ADM2"]:
    level_path = GEO_ROOT / level
    for geojson_file in level_path.glob(f"geoBoundaries-*-{level}.geojson"):
        iso3 = geojson_file.stem.split("-")[1]  # Extrait "BFA" depuis "geoBoundaries-BFA-ADM0.geojson"
        gdf = gpd.read_file(geojson_file)
        print(f"📍 {geojson_file.name} contient {len(gdf)} zones")

        for i, row in gdf.iterrows():
            geom_json = mapping(row.geometry)
            print(f"→ Traitement {iso3}-{level} zone {i}")

            payload = {
                "input": {
                    "bounds": {
                        "geometry": geom_json,
                        "properties": {
                            "crs": "http://www.opengis.net/def/crs/EPSG/0/4326"
                        }
                    },
                    "data": [{
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": "2021-01-01T00:00:00Z",
                                "to": "2025-08-13T23:59:59Z"
                            }
                        }
                    }]
                },
                "aggregation": {
                    "timeRange": {
                        "from": "2021-01-01T00:00:00Z",
                        "to": "2025-08-13T23:59:59Z"
                    },
                    "aggregationInterval": {"of": "P1Y"},
                    "resx": 100,
                    "resy": 100,
                    "evalscript": evalscript
                },
                "statistics": {
                    "ndvi": ["mean", "stDev"],
                    "ndmi": ["mean", "stDev"]
                }
            }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                "https://services.sentinel-hub.com/api/v1/statistics",
                headers=headers,
                json=payload
            )

            if response.ok:
                stats = response.json()
                print(f"✅ {level} {iso3} zone {i} → OK")
                print(json.dumps(stats, indent=2))
            else:
                print(f"❌ {level} {iso3} zone {i} → Error")
                print(response.text)
