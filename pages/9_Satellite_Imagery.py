import streamlit as st
import pandas as pd
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

# 🎯 Streamlit Interface Setup
st.set_page_config(page_title="NDVI Viewer - Sama AgroLink", layout="wide")
st.title("🛰️ NDVI Viewer for Sama AgroLink Africa")
st.markdown("Analyze NDVI dynamically based on field GPS coordinates.")

# 📍 User Input
lat = st.number_input("Latitude", value=11.174, format="%.6f")
lon = st.number_input("Longitude", value=-1.562, format="%.6f")
buffer_m = st.slider("Buffer around field (meters)", 100, 2000, 1000)

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

# ☁️ Cloud Masking Function
def mask_clouds(image):
    qa = image.select('QA60')
    cloud_mask = qa.bitwiseAnd(1 << 10).eq(0)
    return image.updateMask(cloud_mask)

# 📡 NDVI Processing
if st.button("🔍 Generate NDVI"):
    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(buffer_m).bounds()

    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(point) \
        .filterDate(str(start_date), str(end_date)) \
        .map(mask_clouds) \
        .sort('CLOUDY_PIXEL_PERCENTAGE')

    image = collection.first()
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

    # 🖼️ Visualization Parameters
    ndvi_params = {'min': 0, 'max': 1, 'palette': ['red', 'yellow', 'green']}

    # 🗺️ Display Map
    Map = geemap.Map(center=[lat, lon], zoom=12)
    Map.addLayer(ndvi, ndvi_params, 'NDVI')
    Map.addLayer(point, {}, 'Field')
    Map.to_streamlit(height=600)

    # 📥 Downloadable NDVI Image
    url = ndvi.getThumbURL({
        'min': 0,
        'max': 1,
        'region': region,
        'dimensions': 512,
        'format': 'png'
    })
    st.markdown(f"📥 [Download NDVI Image]({url})")

    # 📦 Simulated JSON for Sama AgroLink API
    result_json = {
        "latitude": lat,
        "longitude": lon,
        "crop": crop,
        "agroecological_zone": agro_zone,
        "ndvi_url": url,
        "period": {
            "start": str(start_date),
            "end": str(end_date)
        },
        "recommendation": f"Monitor vegetation for {crop} in the {agro_zone} zone."
    }

    st.subheader("🧪 NDVI Data Output (for Sama AgroLink API)")
    st.code(json.dumps(result_json, indent=2), language='json')
