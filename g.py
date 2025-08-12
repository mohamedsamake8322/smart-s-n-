import requests
import json
import geopandas as gpd # pyright: ignore[reportMissingModuleSource]
from shapely.geometry import mapping # pyright: ignore[reportMissingModuleSource]

# ────────────────────── 🔐 CREDENTIALS ──────────────────────
CLIENT_ID = "e4e33c23-cc62-40c4-b6e1-ef4a0bd9638f"
CLIENT_SECRET = "1VMH5xdZ6tjv06K1ayhCJ5Oo3GE8sv1j"
  # <-- à vérifier

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

token = "TON_TOKEN_ICI"

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

url = "https://services.sentinel-hub.com/api/v1/statistics"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "input": {
        "bounds": {
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[5, 10], [5, 11], [6, 11], [6, 10], [5, 10]]]
            },
            "properties": {"crs": "EPSG:4326"}
        },
        "data": [{
            "type": "sentinel-2-l2a",
            "dataFilter": {
                "timeRange": {
                    "from": "2023-01-01T00:00:00Z",
                    "to": "2023-12-31T23:59:59Z"
                }
            }
        }]
    },
    "aggregation": {
        "timeRange": {
            "from": "2023-01-01T00:00:00Z",
            "to": "2023-12-31T23:59:59Z"
        },
        "aggregationInterval": {"of": "P1Y"},
        "resx": 10,
        "resy": 10
    },
    "evalscript": evalscript,
    "statistics": {
        "ndvi": ["mean", "stDev"],
        "ndmi": ["mean", "stDev"]
    }
}

response = requests.post(url, headers=headers, json=payload)

print(response.status_code)
print(response.text)
