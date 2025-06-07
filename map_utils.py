import folium
import branca
import pandas as pd
import numpy as np

def generate_map():
    """Creates an advanced interactive map with Folium to visualize agricultural zones."""
    map_object = folium.Map(location=[14.692, -17.446], zoom_start=8, tiles="cartodbpositron")
    folium.TileLayer("Stamen Terrain").add_to(map_object)
    folium.TileLayer("Stamen Toner").add_to(map_object)
    folium.TileLayer("Stamen Watercolor").add_to(map_object)
    folium.LayerControl().add_to(map_object)

    zones = [
        {"name": "Optimal Growth Zone", "location": [14.692, -17.446], "color": "blue"},
        {"name": "Moderate Stress Zone", "location": [14.702, -17.456], "color": "orange"},
        {"name": "High-Risk Stress Zone", "location": [14.712, -17.466], "color": "red"},
    ]

    for zone in zones:
        folium.Marker(
            location=zone["location"],
            popup=f"📍 {zone['name']}",
            icon=folium.Icon(color=zone["color"]),
        ).add_to(map_object)

    popup_html = """
    <h3>🌍 Agricultural Field Map</h3>
    <p>Visualization of growth and stress zones for optimized management.</p>
    <p><b>🔵 Optimal Growth Zone</b> - Maximum yield 📈</p>
    <p><b>🟠 Moderate Stress Zone</b> - Adjusted fertilization 🌱</p>
    <p><b>🔴 High-Risk Stress Zone</b> - Urgent intervention 🚨</p>
    """
    folium.Marker(
        [14.695, -17.450], icon=folium.Icon(color="green"),
        popup=branca.element.IFrame(html=popup_html, width=300, height=200)
    ).add_to(map_object)

    return map_object._repr_html_()

def generate_field_map():
    """Creates a field map with interactive markers."""
    field_map = folium.Map(location=[39.9208, 32.8541], zoom_start=6)
    folium.Marker([39.9208, 32.8541], popup="📍 Field Location: Test").add_to(field_map)
    return field_map._repr_html_()

def get_climate_yield_correlation():
    """Simulates the relationship between temperature, humidity, and agricultural yield."""
    data = {
        "temperature": np.random.uniform(15, 35, 50),
        "humidity": np.random.uniform(40, 90, 50),
        "yield": np.random.uniform(3, 10, 50),
    }
    return pd.DataFrame(data)
