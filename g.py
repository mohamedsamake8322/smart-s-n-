import requests
import json
import geopandas as gpd # pyright: ignore[reportMissingModuleSource]

# 🔐 Credentials
CLIENT_ID = "e4e33c23-cc62-40c4-b6e1-ef4a0bkdjhd54f"
CLIENT_SECRET = "1VMH5xdZ6tjv06K1ayhCJ5Oo3G784piu"
INSTANCE_ID = "722f5a09-a6fe-49fc-a5c4-3b465d8c3c23"

# 📍 GADM level1
gdf = gpd.read_file(r"C:\plateforme-agricole-complete-v2\gadm\BFA\level1.geojson")
geom = gdf.geometry[0]
from shapely.geometry import mapping # pyright: ignore[reportMissingModuleSource]
geom_json = mapping(gdf.geometry[0])


# 🧠 Evalscript
evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B08", "B04", "B11", "B02"],
    output: [
      { id: "ndvi", bands: 1 },
      { id: "ndmi", bands: 1 }
    ]
  };
}
function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  let ndmi = (sample.B08 - sample.B11) / (sample.B08 + sample.B11);
  return [ndvi, ndmi];
}
"""
def get_token(client_id, client_secret):
    url = "https://services.sentinel-hub.com/oauth/token"
    payload = {
        "grant_type": "client_credentials",  # ✅ CORRECT
        "client_id": "e4e33c23-cc62-40c4-b6e1-ef4a0bd9638f",
        "client_secret": "1VMH5xdZ6tjv06K1ayhCJ5Oo3GE8sv1j"
    }
    response = requests.post(url, data=payload)
    print("🔍 Réponse brute:", response.text)
    return response.json()["access_token"]

# Tes vraies valeurs ici
CLIENT_ID = "e4e33c23-cc62-40c4-b6e1-ef4a0bd9638f"
CLIENT_SECRET = "1VMH5xdZ6tjv06K1ayhCJ5OrreE8sv1j"
token = get_token(CLIENT_ID, CLIENT_SECRET)
print("✅ Token récupéré:", token)

# 📤 Statistical request
url = "https://services.sentinel-hub.com/api/v1/statistics"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {
    "input": {
        "bounds": {
            "geometry": geom_json,
            "properties": {
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            }
        },
        "data": [{
            "type": "sentinel-2-l2a",
            "dataFilter": {
                "timeRange": {
                    "from": "2023-01-01T00:00:00Z",
                    "to": "2023-12-31T23:59:59Z"
                }
            },
            "processing": {
                "evalscript": evalscript
            }
        }]
    },
    "aggregation": {
        "timeRange": {
            "from": "2023-01-01T00:00:00Z",
            "to": "2023-12-31T23:59:59Z"
        },
        "aggregationInterval": {
            "of": "P1Y"  # P1Y = agrégation annuelle
        },
        "resolution": {
            "width": 512,
            "height": 512
        }
    },
    "calculations": {
        "default": {
            "statistics": {
                "ndvi": {"stats": ["mean", "stDev"]},
                "ndmi": {"stats": ["mean", "stDev"]}
            }
        }
    }
}

url = "https://services.sentinel-hub.com/api/v1/statistics"

response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(json.dumps(result, indent=2))
