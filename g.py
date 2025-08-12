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

token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ3dE9hV1o2aFJJeUowbGlsYXctcWd4NzlUdm1hX3ZKZlNuMW1WNm5HX0tVIn0.eyJleHAiOjE3NTUwMjI3OTAsImlhdCI6MTc1NTAxOTE5MCwianRpIjoiMjhmOWUyNmYtMGQ4ZC00YTA5LTg4OGMtMjc0ODFlZjc1OGMxIiwiaXNzIjoiaHR0cHM6Ly9zZXJ2aWNlcy5zZW50aW5lbC1odWIuY29tL2F1dGgvcmVhbG1zL21haW4iLCJhdWQiOiJodHRwczovL2FwaS5wbGFuZXQuY29tLyIsInN1YiI6ImViY2VlYTY3LTI1MWItNDk4OS1iZWVhLWE3ZDg0ZTNhZDExNSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImU0ZTMzYzIzLWNjNjItNDBjNC1iNmUxLWVmNGEwYmQ5NjM4ZiIsInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2xpZW50SG9zdCI6Ijk1LjIuOS43NSIsInBsX3Byb2plY3QiOiI2ZjZmZmI5NC1mYzRhLTQ2MmYtOTI2NC04ZmVhNGM2YTNlOWYiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzZXJ2aWNlLWFjY291bnQtZTRlMzNjMjMtY2M2Mi00MGM0LWI2ZTEtZWY0YTBiZDk2MzhmIiwiY2xpZW50QWRkcmVzcyI6Ijk1LjIuOS43NSIsImNsaWVudF9pZCI6ImU0ZTMzYzIzLWNjNjItNDBjNC1iNmUxLWVmNGEwYmQ5NjM4ZiIsImFjY291bnQiOiI2ZjZmZmI5NC1mYzRhLTQ2MmYtOTI2NC04ZmVhNGM2YTNlOWYiLCJwbF93b3Jrc3BhY2UiOiJhMjM3YzA1Ny1hZjcwLTQ1ZTUtOTBmNi1jZTE0N2E0N2E1OGMifQ.Q29B2tmO2hrbxy_H-TSTmvD8OnrXoOnL5HUzUDI7TFDIgGI8EyposMr5z84Ynf7X-cWYPXFNifGHZ7Ch_qWUsVYyRL0-2L--D2OhDYs2nLvMwFIWH2Y4qcpscvxvSS-Czd3LfLMUe0lMDVn-3KTuKmt3bna0L9ZnLvQ0fYNEC7rj733BQ4oLg2C_qsZGtJPf2nwuBjUnPlCsnHUGhEjsWIHRJ9Fltjzyc3JkuBCOtynFkmomP7M3QTBjdhq7hpHvj-MDotyyHzHBNm3aOojjO3iR_utriQrAmyzjK7_urm4Bn39WDsjIDhZSEf0Lcp6iqIHo1IdMjfj50CMZSlgvsQ"

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
    "Authorization": f"Bearer {"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ3dE9hV1o2aFJJeUowbGlsYXctcWd4NzlUdm1hX3ZKZlNuMW1WNm5HX0tVIn0.eyJleHAiOjE3NTUwMjI3OTAsImlhdCI6MTc1NTAxOTE5MCwianRpIjoiMjhmOWUyNmYtMGQ4ZC00YTA5LTg4OGMtMjc0ODFlZjc1OGMxIiwiaXNzIjoiaHR0cHM6Ly9zZXJ2aWNlcy5zZW50aW5lbC1odWIuY29tL2F1dGgvcmVhbG1zL21haW4iLCJhdWQiOiJodHRwczovL2FwaS5wbGFuZXQuY29tLyIsInN1YiI6ImViY2VlYTY3LTI1MWItNDk4OS1iZWVhLWE3ZDg0ZTNhZDExNSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImU0ZTMzYzIzLWNjNjItNDBjNC1iNmUxLWVmNGEwYmQ5NjM4ZiIsInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2xpZW50SG9zdCI6Ijk1LjIuOS43NSIsInBsX3Byb2plY3QiOiI2ZjZmZmI5NC1mYzRhLTQ2MmYtOTI2NC04ZmVhNGM2YTNlOWYiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzZXJ2aWNlLWFjY291bnQtZTRlMzNjMjMtY2M2Mi00MGM0LWI2ZTEtZWY0YTBiZDk2MzhmIiwiY2xpZW50QWRkcmVzcyI6Ijk1LjIuOS43NSIsImNsaWVudF9pZCI6ImU0ZTMzYzIzLWNjNjItNDBjNC1iNmUxLWVmNGEwYmQ5NjM4ZiIsImFjY291bnQiOiI2ZjZmZmI5NC1mYzRhLTQ2MmYtOTI2NC04ZmVhNGM2YTNlOWYiLCJwbF93b3Jrc3BhY2UiOiJhMjM3YzA1Ny1hZjcwLTQ1ZTUtOTBmNi1jZTE0N2E0N2E1OGMifQ.Q29B2tmO2hrbxy_H-TSTmvD8OnrXoOnL5HUzUDI7TFDIgGI8EyposMr5z84Ynf7X-cWYPXFNifGHZ7Ch_qWUsVYyRL0-2L--D2OhDYs2nLvMwFIWH2Y4qcpscvxvSS-Czd3LfLMUe0lMDVn-3KTuKmt3bna0L9ZnLvQ0fYNEC7rj733BQ4oLg2C_qsZGtJPf2nwuBjUnPlCsnHUGhEjsWIHRJ9Fltjzyc3JkuBCOtynFkmomP7M3QTBjdhq7hpHvj-MDotyyHzHBNm3aOojjO3iR_utriQrAmyzjK7_urm4Bn39WDsjIDhZSEf0Lcp6iqIHo1IdMjfj50CMZSlgvsQ"}",
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
