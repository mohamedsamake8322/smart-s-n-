import requests
import json
import geopandas as gpd # pyright: ignore[reportMissingModuleSource]
from shapely.geometry import mapping # pyright: ignore[reportMissingModuleSource]

# ────────────────────── 🔐 CREDENTIALS ──────────────────────
CLIENT_ID = "e4e33c23-cc62-40c4-b6e1-ef4a0bd9638f"
CLIENT_SECRET = "1VMH5xdZ6tjv06K1ayhCJ5Oo3GE8sv1j"


# ────────────────────── 📍 LOAD GEOMETRY ──────────────────────
# Exemple avec GADM level1 pour le Burkina Faso
gdf = gpd.read_file(r"C:\plateforme-agricole-complete-v2\gadm\BFA\level1.geojson")
geom_json = mapping(gdf.geometry[0])  # premier polygone

# ────────────────────── 🔑 TOKEN RETRIEVAL ──────────────────────
def get_token(client_id, client_secret):
    url = "https://services.sentinel-hub.com/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    print("Payload envoyé : ", json.dumps(payload, indent=2))
    print("Headers : ", headers)

    response = requests.post(url, data=payload)
    print("🔍 Réponse brute:", response.text)
    response.raise_for_status()
    return response.json()["access_token"]

token = get_token(CLIENT_ID, CLIENT_SECRET)
print("✅ Token récupéré:", token)

# ────────────────────── 🧠 EVALSCRIPT ──────────────────────
# Cet evalscript calcule NDVI et NDMI
evalscript = (
    "//VERSION=3\n"
    "function setup() {\n"
    "  return {\n"
    "    input: [\"B08\", \"B04\", \"B11\"],\n"
    "    output: [\n"
    "      { id: \"ndvi\", bands: 1, sampleType: \"FLOAT32\" },\n"
    "      { id: \"ndmi\", bands: 1, sampleType: \"FLOAT32\" }\n"
    "    ]\n"
    "  };\n"
    "}\n"
    "function evaluatePixel(sample) {\n"
    "  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);\n"
    "  let ndmi = (sample.B08 - sample.B11) / (sample.B08 + sample.B11);\n"
    "  return {\n"
    "    ndvi: [ndvi],\n"
    "    ndmi: [ndmi]\n"
    "  };\n"
    "}\n"
)



# ────────────────────── 📤 STATISTICS REQUEST ──────────────────────
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
                "crs": "EPSG:4326"
            }
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
        "aggregationInterval": {
            "of": "P1Y"
        },
        "resx": 10,
        "resy": 10
    },
    "calculations": {
        "default": {
            "script": evalscript,
            "statistics": {
                "ndvi": ["mean", "stDev"],
                "ndmi": ["mean", "stDev"]
            }
        }
    }
}


# ────────────────────── 📥 SEND REQUEST ──────────────────────
response = requests.post(url, headers=headers, json=payload)

try:
    response.raise_for_status()
    result = response.json()
    print(json.dumps(result, indent=2))
except requests.exceptions.HTTPError:
    print(f"Erreur HTTP {response.status_code} : {response.text}")
