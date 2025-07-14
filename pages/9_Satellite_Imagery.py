import streamlit as st
import pandas as pd
import geopandas as gpd
import ee
import geemap.foliumap as geemap
import datetime
import json

# 🔐 Authenticate Earth Engine
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# 🌍 Load GeoJSON regions
regions = gpd.read_file("africa_admin_level2.geojson")

# 🧪 Load Soil Profile
df_soil = pd.read_csv("soil_profile_africa.csv")
soil_gdf = gpd.GeoDataFrame(df_soil, geometry=gpd.points_from_xy(df_soil.x, df_soil.y), crs="EPSG:4326")
soil_cols = [col for col in df_soil.columns if "_" in col and col != "geometry"]

# 🎯 Streamlit Setup
st.set_page_config(page_title="NDVI + Soil Viewer - Sama AgroLink", layout="wide")
st.title("🛰️ NDVI & Soil Viewer for Sama AgroLink Africa")

mode = st.radio("NDVI Target Mode", ["GPS Coordinates", "Administrative Region"])

if mode == "GPS Coordinates":
    lat = st.number_input("Latitude", value=11.174, format="%.6f")
    lon = st.number_input("Longitude", value=-1.562, format="%.6f")
    buffer_m = st.slider("Buffer around field (meters)", 100, 2000, 1000)
    geometry = ee.Geometry.Point([lon, lat]).buffer(buffer_m).bounds()
    poly_geom = gpd.GeoSeries([gpd.points_from_xy([lon], [lat])[0].buffer(buffer_m/111000)], crs="EPSG:4326")
else:
    countries = sorted(regions["GID_0"].dropna().unique())
    selected_country = st.selectbox("Country", countries)
    filtered = regions[regions["GID_0"] == selected_country]
    region_names = sorted(filtered["NAME_2"].dropna().unique())
    selected_region = st.selectbox("Region", region_names)
    selected_geom = filtered[filtered["NAME_2"] == selected_region].geometry.iloc[0]
    bounds = selected_geom.bounds
    minx, miny, maxx, maxy = bounds
    geometry = ee.Geometry.Rectangle([minx, miny, maxx, maxy])
    poly_geom = gpd.GeoSeries([selected_geom], crs="EPSG:4326")

start_date = st.date_input("Start Date", value=datetime.date(2023, 6, 1))
end_date = st.date_input("End Date", value=datetime.date(2023, 7, 1))

crop = st.selectbox("Crop Type", ["Maize", "Rice", "Millet", "Cotton", "Sorghum",
"Wheat", "Barley", "Oats", "Rye", "Fonio", "Triticale",
"Tomato", "Potato", "Carrot", "Onion", "Garlic",
"Cucumber", "Spinach", "Lettuce", "Cabbage", "Peas",
"Sweet Pepper", "Eggplant", "Zucchini", "Cauliflower",
"Pumpkin", "Okra", "Radish", "Beetroot", "Broccoli",
"Soybean", "Sunflower", "Rapeseed", "Groundnut",
"Sesame", "Olive", "Flaxseed", "Castor", "Safflower",
"Hemp", "Oil Palm",
"Apple", "Pear", "Orange", "Lemon", "Lime", "Mango",
"Banana", "Avocado", "Papaya", "Peach", "Plum",
"Cherry", "Apricot", "Pomegranate", "Fig", "Grapefruit",
"Grape", "Date", "Coconut",
"Tea", "Coffee", "Sugarcane", "Tobacco", "Vanilla",
"Pineapple", "Guava", "Passionfruit", "Lychee", "Kiwi",
"Artichoke", "Asparagus", "Chili Pepper", "Turnip",
"Yam", "Taro", "Cassava", "Leek", "Celery", "Mustard",
"Mulberry", "Blackberry", "Blueberry", "Raspberry",
"Strawberry", "Chestnut", "Walnut", "Almond", "Hazelnut",
"Macadamia", "Pistachio"])
agro_zone = st.text_input("Agroecological Zone (e.g. Sudan West)", "Sudan West")

# ☁️ Cloud Masking
selected_soil_col = st.selectbox("Soil Property to Display", soil_cols)

# ☁️ Cloud Masking
def mask_clouds(image):
    qa = image.select('QA60')
    cloud_mask = qa.bitwiseAnd(1 << 10).eq(0)
    return image.updateMask(cloud_mask)

if st.button("🔍 Generate NDVI + Soil Map"):
    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(geometry) \
        .filterDate(str(start_date), str(end_date)) \
        .map(mask_clouds) \
        .sort("CLOUDY_PIXEL_PERCENTAGE")

    image = collection.first()
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    ndvi_params = {'min': 0, 'max': 1, 'palette': ['red', 'yellow', 'green']}

    if mode == "GPS Coordinates":
        Map = geemap.Map(center=[lat, lon], zoom=12)
        Map.addLayer(ee.Geometry.Point([lon, lat]), {}, 'Field')
    else:
        center_lat = (miny + maxy) / 2
        center_lon = (minx + maxx) / 2
        Map = geemap.Map(center=[center_lat, center_lon], zoom=6)
        Map.addLayer(selected_geom.__geo_interface__, {}, 'Selected Region')

    Map.addLayer(ndvi, ndvi_params, 'NDVI')

    # 🧭 Soil data overlay
    soil_within = soil_gdf[soil_gdf.within(poly_geom.iloc[0])]
    Map.add_points_from_xy(
        soil_within,
        column=selected_soil_col,
        color_column=selected_soil_col,
        color_palette="viridis",
        layer_name=f"Soil: {selected_soil_col}",
        radius=5,
        info_mode="on_hover"
    )

    Map.to_streamlit(height=600)

    url = ndvi.getThumbURL({
        'min': 0,
        'max': 1,
        'region': geometry,
        'dimensions': 512,
        'format': 'png'
    })
    st.markdown(f"📥 [Download NDVI Image]({url})")

    # 📊 Soil stats
    soil_stats = soil_within.mean(numeric_only=True).to_dict()

    result_json = {
        "mode": mode,
        "latitude": lat if mode == "GPS Coordinates" else None,
        "longitude": lon if mode == "GPS Coordinates" else None,
        "country": selected_country if mode == "Administrative Region" else None,
        "region": selected_region if mode == "Administrative Region" else None,
        "crop": crop,
        "agroecological_zone": agro_zone,
        "ndvi_url": url,
        "period": {
            "start": str(start_date),
            "end": str(end_date)
        },
        "soil_property": selected_soil_col,
        "soil_profile": soil_stats,
        "recommendation": f"Monitor vegetation for {crop} in the {agro_zone} zone. Soil {selected_soil_col} may influence response."
    }

    st.subheader("🧪 NDVI + Soil Data Output (for Sama AgroLink API)")
    st.code(json.dumps(result_json, indent=2), language='json')
