import requests
import json
import geopandas as gpd
from shapely.geometry import mapping

# 🔐 Credentials
CLIENT_ID = "e4e33c23-cc62-40c4-b6e1-ef4a0bd9638f"
CLIENT_SECRET = "1VMH5xdZ6tjv06K1ayhCJ5Oo3GE8sv1j"

# 📍 GADM level1
gdf = gpd.read_file(r"C:\plateforme-agricole-complete-v2\gadm\BFA\level1.geojson")
geom_json = mapping(gdf.geometry[0])

# 🔑 Token retrieval
def get_token(client_id, client_secret):
    url = "https://services.sentinel-hub.com/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": "e4e33c23-cc62-40c4-b6e1-ef4a0bd9638f",
        "client_secret": "1VMH5xdZ6tjv06K1ayhCJ5Oo3GE8sv1j"
    }
    response = requests.post(url, data=payload)
    print("🔍 Réponse brute:", response.text)
    return response.json()["access_token"]

token = get_token(CLIENT_ID, CLIENT_SECRET)
print("✅ Token récupéré:", token)

# 🧠 Evalscript
evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B08", "B04", "B11"],
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
            "of": "P1Y"
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

response = requests.post(url, headers=headers, json=payload)
result = response.json()
print(json.dumps(result, indent=2))
