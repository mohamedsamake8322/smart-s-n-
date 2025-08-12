import os
import geopandas as gpd # type: ignore
import pandas as pd
from sentinelhub import ( # pyright: ignore[reportMissingImports]
    SHConfig, Geometry, CRS, SentinelHubStatistical, StatisticalRequest, DataCollection
)

# 📍 Dossiers
GADM_ROOT = r"C:\plateforme-agricole-complete-v2\gadm"
OUTPUT_ROOT = r"C:\plateforme-agricole-complete-v2\ndvi_statistical"

# 🔐 Credentials
config = SHConfig()
config.instance_id = "722f5a09-a6fe-49fc-a5c4-3b465d8c3c23"
config.sh_client_id = "e4e33c23-cc62-40c4-b6e1-ef4a0bd9638f"
config.sh_client_secret = "1VMH5xdZ6tjv06K1ayhCJ5Oo3GE8sv1j"

# 🧠 Evalscript NDVI + NDMI avec masque nuage
evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "B11", "CLM"],
    output: [
      { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
      { id: "ndmi", bands: 1, sampleType: "FLOAT32" }
    ]
  };
}
function evaluatePixel(sample) {
  if (sample.CLM == 1) {
    return { ndvi: [NaN], ndmi: [NaN] };
  }
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  let ndmi = (sample.B08 - sample.B11) / (sample.B08 + sample.B11);
  return { ndvi: [ndvi], ndmi: [ndmi] };
}
"""

def process_country(country_code):
    country_path = os.path.join(GADM_ROOT, country_code)
    level1_path = os.path.join(country_path, "level1.geojson")
    if not os.path.exists(level1_path):
        print(f"❌ Aucun level1 pour {country_code}")
        return

    gadm1 = gpd.read_file(level1_path)
    output_dir = os.path.join(OUTPUT_ROOT, country_code)
    os.makedirs(output_dir, exist_ok=True)

    for year in range(2021, 2026):
        records = []
        for i, row in gadm1.iterrows():
            name = row.get("NAME_1", f"region_{i}")
            gid = row.get("GID_1", f"GID_{i}")
            geom = Geometry(row.geometry.to_wkt(), CRS.WGS84)

            request = StatisticalRequest(
                input_data=[{
                    "dataCollection": DataCollection.SENTINEL2_L2A,
                    "timeRange": {
                        "from": f"{year}-01-01T00:00:00Z",
                        "to": f"{year}-12-31T23:59:59Z"
                    },
                    "processing": {"evalscript": evalscript}
                }],
                aggregation={
                    "timeAggregation": "YEAR",
                    "aggregationInterval": {
                        "from": f"{year}-01-01",
                        "to": f"{year}-12-31"
                    },
                    "resolution": {"width": 512, "height": 512}
                },
                geometry=geom,
                calculations={
                    "default": {
                        "statistics": {
                            "ndvi": {"stats": ["mean", "stDev"]},
                            "ndmi": {"stats": ["mean", "stDev"]}
                        }
                    }
                },
                config=config
            )

            try:
                response = request.get_data()
                stats = response['data'][0]['outputs']['default']['bands']
                records.append({
                    "year": year,
                    "GID_1": gid,
                    "NAME_1": name,
                    "NDVI_mean": stats['ndvi']['stats']['mean'],
                    "NDVI_std": stats['ndvi']['stats']['stDev'],
                    "NDMI_mean": stats['ndmi']['stats']['mean'],
                    "NDMI_std": stats['ndmi']['stats']['stDev']
                })
            except Exception as e:
                print(f"⚠️ Erreur pour {name} ({year}) → {e}")

        # Sauvegarde
        df = pd.DataFrame(records)
        output_file = os.path.join(output_dir, f"{country_code}_{year}_stats.csv.gz")
        df.to_csv(output_file, index=False, compression="gzip")
        print(f"✅ {country_code} {year} exporté → {output_file}")

def run_statistical_pipeline():
    for country_code in os.listdir(GADM_ROOT):
        country_path = os.path.join(GADM_ROOT, country_code)
        if os.path.isdir(country_path):
            print(f"\n🌍 Traitement de {country_code}")
            process_country(country_code)

if __name__ == "__main__":
    run_statistical_pipeline()
