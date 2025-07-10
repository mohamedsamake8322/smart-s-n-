import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from utils.weather_api import WeatherAPI
from config.translator import translate_text


st.set_page_config(page_title="Weather Data", page_icon="🌤️", layout="wide")

st.title("🌤️ Weather Data Integration")
st.markdown("### Real-time and historical weather information for agricultural planning")

# Initialize weather API
if 'weather_api' not in st.session_state:
    st.session_state.weather_api = WeatherAPI()

weather_api = st.session_state.weather_api

# Sidebar for location settings
st.sidebar.title("Location Settings")

# Location input
location_method = st.sidebar.radio(
    "Select Location Method",
    ["City Name", "Coordinates"],
    help="Choose how to specify location for weather data"
)

if location_method == "City Name":
    city = st.sidebar.text_input(
        "City Name",
        value="New York",
        help="Enter city name for weather data"
    )
    country = st.sidebar.text_input(
        "Country Code (optional)",
        value="US",
        help="2-letter country code (e.g., US, UK, CA)"
    )
    location_key = f"{city},{country}" if country else city
else:
    lat = st.sidebar.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=40.7128,
        format="%.4f"
    )
    lon = st.sidebar.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=-74.0060,
        format="%.4f"
    )
    location_key = f"{lat},{lon}"

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["Current Weather", "Forecast", "Historical Data", "Agricultural Insights"])

with tab1:
    st.subheader("Current Weather Conditions")

    col1, col2 = st.columns([2, 1])

    with col2:
        if st.button("🔄 Refresh Weather Data", use_container_width=True):
            st.session_state.weather_data = None

    # Get current weather data
    if st.button("📡 Get Current Weather", use_container_width=True) or 'current_weather' not in st.session_state:
        with st.spinner("Fetching current weather data..."):
            current_weather = weather_api.get_current_weather(location_key)

            if current_weather:
                st.session_state.current_weather = current_weather
            else:
                st.error("Unable to fetch weather data. Please check your location and try again.")

    # Display current weather
    if 'current_weather' in st.session_state:
        weather = st.session_state.current_weather

        # Main weather display
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Temperature",
                f"{weather.get('temperature', 'N/A')}°C",
                delta=f"Feels like {weather.get('feels_like', 'N/A')}°C"
            )

        with col2:
            st.metric(
                "Humidity",
                f"{weather.get('humidity', 'N/A')}%",
                help="Relative humidity percentage"
            )

        with col3:
            st.metric(
                "Wind Speed",
                f"{weather.get('wind_speed', 'N/A')} km/h",
                delta=f"{weather.get('wind_direction', 'N/A')}"
            )

        with col4:
            st.metric(
                "Pressure",
                f"{weather.get('pressure', 'N/A')} hPa",
                help="Atmospheric pressure"
            )

        # Additional weather details
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Weather Conditions**")
            st.write(f"☁️ **Condition:** {weather.get('description', 'N/A').title()}")
            st.write(f"👁️ **Visibility:** {weather.get('visibility', 'N/A')} km")
            st.write(f"☀️ **UV Index:** {weather.get('uv_index', 'N/A')}")

        with col2:
            st.markdown("**Agricultural Relevance**")

            # Agricultural insights based on current conditions
            temp = weather.get('temperature', 0)
            humidity = weather.get('humidity', 0)

            if temp < 5:
                st.warning("🥶 Risk of frost - protect sensitive crops")
            elif temp > 35:
                st.warning("🔥 High temperature - ensure adequate irrigation")
            else:
                st.success("🌡️ Temperature suitable for most crops")

            if humidity < 30:
                st.warning("🏜️ Low humidity - consider irrigation")
            elif humidity > 80:
                st.warning("💧 High humidity - monitor for fungal diseases")
            else:
                st.success("💨 Humidity levels optimal")

with tab2:
    st.subheader("Weather Forecast")

    # Forecast period selection
    forecast_days = st.selectbox(
        "Forecast Period",
        [3, 5, 7, 10],
        index=1,
        help="Number of days to forecast"
    )

    if st.button("📅 Get Weather Forecast", use_container_width=True):
        with st.spinner("Fetching weather forecast..."):
            forecast_data = weather_api.get_forecast(location_key, forecast_days)

            if forecast_data:
                st.session_state.forecast_data = forecast_data
            else:
                st.error("Unable to fetch forecast data.")

    # Display forecast
    if 'forecast_data' in st.session_state:
        forecast = st.session_state.forecast_data

        # Convert to DataFrame for better visualization
        if isinstance(forecast, list) and len(forecast) > 0:
            forecast_df = pd.DataFrame(forecast)

            # Temperature trend chart
            if 'date' in forecast_df.columns and 'temperature_max' in forecast_df.columns:
                fig_temp = go.Figure()

                fig_temp.add_trace(go.Scatter(
                    x=forecast_df['date'],
                    y=forecast_df['temperature_max'],
                    mode='lines+markers',
                    name='Max Temperature',
                    line=dict(color='red')
                ))

                fig_temp.add_trace(go.Scatter(
                    x=forecast_df['date'],
                    y=forecast_df['temperature_min'],
                    mode='lines+markers',
                    name='Min Temperature',
                    line=dict(color='blue'),
                    fill='tonexty'
                ))

                fig_temp.update_layout(
                    title="Temperature Forecast",
                    xaxis_title="Date",
                    yaxis_title="Temperature (°C)"
                )
                st.plotly_chart(fig_temp, use_container_width=True)

            # Precipitation forecast
            if 'precipitation' in forecast_df.columns:
                fig_precip = px.bar(
                    forecast_df,
                    x='date',
                    y='precipitation',
                    title="Precipitation Forecast",
                    labels={'precipitation': 'Precipitation (mm)', 'date': 'Date'}
                )
                st.plotly_chart(fig_precip, use_container_width=True)

            # Forecast table
            st.markdown("**Detailed Forecast**")
            display_cols = ['date', 'temperature_max', 'temperature_min', 'humidity', 'precipitation', 'description']
            available_cols = [col for col in display_cols if col in forecast_df.columns]

            if available_cols:
                st.dataframe(forecast_df[available_cols], use_container_width=True)
        else:
            st.warning("Forecast data format not recognized or empty.")

with tab3:
    st.subheader("Historical Weather Data")

    # Date range selection
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30),
            max_value=datetime.now().date()
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date(),
            max_value=datetime.now().date()
        )

    if start_date >= end_date:
        st.error("Start date must be before end date.")
    else:
        if st.button("📊 Get Historical Data", use_container_width=True):
            with st.spinner("Fetching historical weather data..."):
                historical_data = weather_api.get_historical_data(location_key, start_date, end_date)

                if historical_data:
                    st.session_state.historical_data = historical_data
                else:
                    st.error("Unable to fetch historical data.")

        # Display historical data
        if 'historical_data' in st.session_state:
            historical = st.session_state.historical_data

            if isinstance(historical, list) and len(historical) > 0:
                hist_df = pd.DataFrame(historical)

                # Temperature trends
                if 'date' in hist_df.columns and 'temperature' in hist_df.columns:
                    fig_hist_temp = px.line(
                        hist_df,
                        x='date',
                        y='temperature',
                        title="Historical Temperature Trend",
                        labels={'temperature': 'Temperature (°C)', 'date': 'Date'}
                    )
                    st.plotly_chart(fig_hist_temp, use_container_width=True)

                # Precipitation history
                if 'precipitation' in hist_df.columns:
                    fig_hist_precip = px.bar(
                        hist_df,
                        x='date',
                        y='precipitation',
                        title="Historical Precipitation",
                        labels={'precipitation': 'Precipitation (mm)', 'date': 'Date'}
                    )
                    st.plotly_chart(fig_hist_precip, use_container_width=True)

                # Statistical summary
                st.markdown("**Statistical Summary**")
                numeric_cols = hist_df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    st.dataframe(hist_df[numeric_cols].describe(), use_container_width=True)
            else:
                st.warning("No historical data available for the selected period.")

with tab4:
    st.subheader("Agricultural Weather Insights")

    # Weather-based agricultural recommendations
    st.markdown("**Weather-Based Agricultural Recommendations**")

    if 'current_weather' in st.session_state:
        weather = st.session_state.current_weather

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Current Conditions Analysis**")

            temp = weather.get('temperature', 0)
            humidity = weather.get('humidity', 0)
            wind_speed = weather.get('wind_speed', 0)

            # Growing degree days calculation
            base_temp = 10  # Base temperature for most crops
            if temp > base_temp:
                gdd = temp - base_temp
                st.metric("Growing Degree Days", f"{gdd:.1f}", help="Heat units available for crop growth")

            # Evapotranspiration estimate
            if temp > 0 and humidity > 0:
                # Simplified ET calculation
                et_estimate = max(0, (temp - 5) * (1 - humidity/100) * 0.1)
                st.metric("Est. Evapotranspiration", f"{et_estimate:.2f} mm/day", help="Estimated water loss")

        with col2:
            st.markdown("**Recommendations**")

            recommendations = []

            # Temperature-based recommendations
            if temp < 0:
                recommendations.append("❄️ Risk of freezing - protect crops with covers")
            elif temp < 5:
                recommendations.append("🥶 Cold conditions - delay planting of warm-season crops")
            elif temp > 30:
                recommendations.append("🌡️ Hot conditions - increase irrigation frequency")
                recommendations.append("☂️ Provide shade for sensitive crops")

            # Humidity-based recommendations
            if humidity > 85:
                recommendations.append("💧 High humidity - monitor for fungal diseases")
                recommendations.append("🌬️ Ensure good air circulation")
            elif humidity < 40:
                recommendations.append("🏜️ Low humidity - increase irrigation")

            # Wind-based recommendations
            if wind_speed > 25:
                recommendations.append("💨 Strong winds - secure plant supports")
                recommendations.append("🛡️ Consider windbreaks for protection")

            if not recommendations:
                recommendations.append("✅ Weather conditions are favorable for most agricultural activities")

            for rec in recommendations:
                st.write(rec)

    # Seasonal planning
    st.markdown("---")
    st.subheader("Seasonal Planning Tools")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Crop Calendar Integration**")

        crop_type = st.selectbox(
            "Select Crop for Planning",
            ["Wheat", "Corn", "Rice", "Soybeans", "Tomatoes", "Potatoes"]
        )

        # Sample crop requirements (in a real app, this would be from a database)
        crop_requirements = {
            "Wheat": {"min_temp": 3, "max_temp": 32, "rainfall": "300-400mm"},
            "Corn": {"min_temp": 10, "max_temp": 35, "rainfall": "500-800mm"},
            "Rice": {"min_temp": 20, "max_temp": 37, "rainfall": "1000-2000mm"},
            "Soybeans": {"min_temp": 10, "max_temp": 35, "rainfall": "450-700mm"},
            "Tomatoes": {"min_temp": 15, "max_temp": 29, "rainfall": "400-600mm"},
            "Potatoes": {"min_temp": 7, "max_temp": 24, "rainfall": "400-600mm"}
        }

        if crop_type in crop_requirements:
            req = crop_requirements[crop_type]
            st.write(f"**{crop_type} Requirements:**")
            st.write(f"• Temperature: {req['min_temp']}°C - {req['max_temp']}°C")
            st.write(f"• Water needs: {req['rainfall']}")

    with col2:
        st.markdown("**Weather Alerts**")

        # Configurable weather alerts
        temp_threshold = st.slider("Temperature Alert (°C)", -10, 45, 35)
        precip_threshold = st.slider("Precipitation Alert (mm)", 0, 100, 50)

        if 'current_weather' in st.session_state:
            current_temp = st.session_state.current_weather.get('temperature', 0)

            if current_temp > temp_threshold:
                st.warning(f"🚨 Temperature alert: {current_temp}°C exceeds threshold of {temp_threshold}°C")
            else:
                st.success("✅ Temperature within acceptable range")
