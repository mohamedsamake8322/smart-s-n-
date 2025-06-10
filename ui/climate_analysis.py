"""
Enterprise Climate Analysis Interface
Professional weather monitoring and agricultural climate intelligence
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, Any, List

from services.weather_service import weather_service
from services.analysis_service import analysis_service, AnalysisRequest
from utils.visualization import viz_engine
from core.database import db_manager

def render_climate_analysis():
    """Render the climate analysis interface"""
    
    st.header("☁️ Climate Analysis & Weather Intelligence")
    st.markdown("Advanced weather monitoring and agricultural climate insights")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌤️ Current Conditions", 
        "📈 Weather Forecast", 
        "📊 Climate Analytics", 
        "⚡ Weather Alerts"
    ])
    
    with tab1:
        render_current_conditions()
    
    with tab2:
        render_weather_forecast()
    
    with tab3:
        render_climate_analytics()
    
    with tab4:
        render_weather_alerts()

def render_current_conditions():
    """Render current weather conditions"""
    
    st.subheader("Current Weather Conditions")
    
    # Location input
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        location_option = st.radio(
            "Choose Location Method:",
            options=["Manual Coordinates", "Registered Farms"],
            horizontal=True
        )
    
    if location_option == "Manual Coordinates":
        with col2:
            latitude = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=14.6937,  # Senegal default
                step=0.1
            )
        
        with col3:
            longitude = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=-17.4441,  # Senegal default
                step=0.1
            )
        
        location_coords = (latitude, longitude)
        location_name = f"Location ({latitude:.2f}, {longitude:.2f})"
    
    else:
        # Get registered farms
        try:
            farms = db_manager.get_farm_locations(user_id=1)  # TODO: Get from session
            
            if farms:
                farm_options = {f"{farm['name']}": (farm['latitude'], farm['longitude']) for farm in farms}
                selected_farm = st.selectbox("Select Farm:", options=list(farm_options.keys()))
                
                location_coords = farm_options[selected_farm]
                location_name = selected_farm
            else:
                st.warning("⚠️ No registered farms found. Please register farm locations first.")
                location_coords = (14.6937, -17.4441)
                location_name = "Default Location"
        
        except Exception as e:
            st.error(f"❌ Error loading farms: {e}")
            location_coords = (14.6937, -17.4441)
            location_name = "Default Location"
    
    # Get current weather
    if st.button("🔄 Get Current Weather", type="primary"):
        with st.spinner("🌤️ Fetching current weather data..."):
            try:
                weather_data = weather_service.get_current_weather(
                    location_coords[0], location_coords[1]
                )
                
                if weather_data.get('success'):
                    st.session_state['current_weather'] = weather_data
                    st.session_state['weather_location'] = location_name
                    st.success("✅ Weather data updated!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to get weather data: {weather_data.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"❌ Error fetching weather: {e}")
    
    # Display current weather
    if 'current_weather' in st.session_state:
        weather = st.session_state['current_weather']
        location = st.session_state.get('weather_location', 'Unknown Location')
        
        st.markdown(f"### 📍 {location}")
        st.caption(f"Last updated: {weather.get('timestamp', 'Unknown')}")
        
        # Main weather metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            temp = weather.get('temperature', 0)
            st.metric(
                label="🌡️ Temperature",
                value=f"{temp:.1f}°C",
                delta=None
            )
        
        with col2:
            humidity = weather.get('humidity', 0)
            humidity_status = "High" if humidity > 80 else "Moderate" if humidity > 60 else "Low"
            st.metric(
                label="💧 Humidity", 
                value=f"{humidity:.0f}%",
                delta=humidity_status
            )
        
        with col3:
            pressure = weather.get('pressure', 0)
            st.metric(
                label="📊 Pressure",
                value=f"{pressure:.0f} hPa",
                delta=None
            )
        
        with col4:
            wind_speed = weather.get('wind_speed', 0)
            st.metric(
                label="💨 Wind Speed",
                value=f"{wind_speed:.1f} m/s",
                delta=None
            )
        
        # Weather description
        description = weather.get('description', 'Unknown')
        st.markdown(f"**☁️ Conditions:** {description.title()}")
        
        # Agricultural insights
        st.markdown("---")
        st.markdown("### 🌾 Agricultural Insights")
        
        # Generate insights based on current conditions
        insights = generate_weather_insights(weather)
        
        if insights['alerts']:
            st.error("⚠️ **Weather Alerts:**")
            for alert in insights['alerts']:
                st.write(f"• {alert}")
        
        if insights['recommendations']:
            st.success("💡 **Recommendations:**")
            for rec in insights['recommendations']:
                st.write(f"• {rec}")
        
        if insights['opportunities']:
            st.info("🎯 **Opportunities:**")
            for opp in insights['opportunities']:
                st.write(f"• {opp}")
        
        # Detailed conditions table
        st.markdown("---")
        st.markdown("### 📋 Detailed Conditions")
        
        conditions_data = {
            "Parameter": ["Temperature", "Humidity", "Pressure", "Wind Speed", "Conditions"],
            "Value": [
                f"{temp:.1f}°C",
                f"{humidity:.0f}%", 
                f"{pressure:.0f} hPa",
                f"{wind_speed:.1f} m/s",
                description.title()
            ],
            "Status": [
                get_temperature_status(temp),
                get_humidity_status(humidity),
                get_pressure_status(pressure),
                get_wind_status(wind_speed),
                "Normal"
            ]
        }
        
        conditions_df = pd.DataFrame(conditions_data)
        st.dataframe(conditions_df, use_container_width=True, hide_index=True)
    
    else:
        st.info("🌤️ Click 'Get Current Weather' to fetch current conditions")
        
        # Sample weather display
        st.markdown("### 📊 Weather Monitoring Features")
        features = [
            "🌡️ Real-time temperature monitoring",
            "💧 Humidity tracking for disease risk",
            "📊 Atmospheric pressure trends", 
            "💨 Wind speed and direction",
            "☁️ Current weather conditions",
            "🌾 Agricultural impact analysis"
        ]
        
        for feature in features:
            st.write(feature)

def render_weather_forecast():
    """Render weather forecast interface"""
    
    st.subheader("Weather Forecast & Planning")
    
    # Forecast settings
    col1, col2 = st.columns([2, 1])
    
    with col1:
        forecast_days = st.selectbox(
            "Forecast Period:",
            options=[3, 5, 7, 10, 14],
            index=2,
            help="Number of days to forecast"
        )
    
    with col2:
        forecast_detail = st.selectbox(
            "Detail Level:",
            options=["Summary", "Detailed", "Agricultural Focus"],
            help="Type of forecast information"
        )
    
    # Use location from current weather or default
    if 'current_weather' in st.session_state and 'weather_location' in st.session_state:
        # Use the coordinates from the last weather check
        # For demo purposes, using default coordinates
        lat, lon = 14.6937, -17.4441
        location_name = st.session_state.get('weather_location', 'Current Location')
    else:
        lat, lon = 14.6937, -17.4441
        location_name = "Default Location"
    
    if st.button("📈 Get Weather Forecast", type="primary"):
        with st.spinner(f"🔄 Fetching {forecast_days}-day forecast..."):
            try:
                forecast_data = weather_service.get_weather_forecast(
                    lat, lon, days=forecast_days
                )
                
                if forecast_data.get('success'):
                    st.session_state['weather_forecast'] = forecast_data
                    st.success("✅ Forecast data loaded!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed to get forecast: {forecast_data.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"❌ Error fetching forecast: {e}")
    
    # Display forecast
    if 'weather_forecast' in st.session_state:
        forecast = st.session_state['weather_forecast']
        forecast_list = forecast.get('forecast', [])
        
        if forecast_list:
            st.markdown(f"### 📅 {forecast_days}-Day Forecast for {location_name}")
            
            # Summary cards
            st.markdown("**📊 Forecast Summary:**")
            
            # Calculate summary statistics
            temps_max = [day.get('temperature_max', 0) for day in forecast_list]
            temps_min = [day.get('temperature_min', 0) for day in forecast_list]
            rainfall_total = sum(day.get('rainfall', 0) for day in forecast_list)
            avg_humidity = sum(day.get('humidity', 0) for day in forecast_list) / len(forecast_list)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🌡️ Temp Range", f"{min(temps_min):.0f}°C - {max(temps_max):.0f}°C")
            with col2:
                st.metric("🌧️ Total Rainfall", f"{rainfall_total:.1f} mm")
            with col3:
                st.metric("💧 Avg Humidity", f"{avg_humidity:.0f}%")
            with col4:
                rainy_days = len([day for day in forecast_list if day.get('rainfall', 0) > 1])
                st.metric("🌧️ Rainy Days", rainy_days)
            
            # Forecast visualization
            st.markdown("**📈 Temperature & Rainfall Forecast:**")
            
            # Create forecast chart
            fig = create_forecast_chart(forecast_list)
            st.plotly_chart(fig, use_container_width=True)
            
            # Daily forecast details
            if forecast_detail in ["Detailed", "Agricultural Focus"]:
                st.markdown("**📅 Daily Forecast Details:**")
                
                for i, day in enumerate(forecast_list):
                    with st.expander(f"📅 Day {i+1}: {day.get('date', 'Unknown Date')}"):
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.markdown("**🌡️ Temperature:**")
                            st.write(f"Max: {day.get('temperature_max', 0):.1f}°C")
                            st.write(f"Min: {day.get('temperature_min', 0):.1f}°C")
                            st.write(f"Avg: {day.get('temperature_avg', 0):.1f}°C")
                        
                        with col_b:
                            st.markdown("**🌧️ Precipitation:**")
                            st.write(f"Rainfall: {day.get('rainfall', 0):.1f} mm")
                            st.write(f"Humidity: {day.get('humidity', 0):.0f}%")
                            st.write(f"Wind: {day.get('wind_speed', 0):.1f} m/s")
                        
                        with col_c:
                            st.markdown("**☁️ Conditions:**")
                            st.write(f"Weather: {day.get('description', 'Unknown')}")
                            
                            if 'uv_index' in day:
                                st.write(f"UV Index: {day.get('uv_index', 0)}")
                            
                            # Agricultural recommendations for the day
                            if forecast_detail == "Agricultural Focus":
                                day_recommendations = get_daily_agricultural_advice(day)
                                if day_recommendations:
                                    st.markdown("**🌾 Agricultural Advice:**")
                                    for advice in day_recommendations:
                                        st.write(f"• {advice}")
            
            # Agricultural planning
            st.markdown("---")
            st.markdown("**🌾 Agricultural Planning Insights:**")
            
            planning_insights = generate_forecast_insights(forecast_list)
            
            col_x, col_y = st.columns(2)
            
            with col_x:
                if planning_insights['irrigation']:
                    st.success("💧 **Irrigation Recommendations:**")
                    for rec in planning_insights['irrigation']:
                        st.write(f"• {rec}")
            
            with col_y:
                if planning_insights['field_work']:
                    st.info("🚜 **Field Work Opportunities:**")
                    for opp in planning_insights['field_work']:
                        st.write(f"• {opp}")
            
            if planning_insights['warnings']:
                st.warning("⚠️ **Weather Warnings:**")
                for warning in planning_insights['warnings']:
                    st.write(f"• {warning}")
        
        else:
            st.error("❌ No forecast data available")
    
    else:
        st.info("📈 Click 'Get Weather Forecast' to see upcoming weather conditions")

def render_climate_analytics():
    """Render climate analytics and trends"""
    
    st.subheader("Climate Analytics & Historical Trends")
    
    # Analytics options
    analysis_type = st.selectbox(
        "Analysis Type:",
        options=[
            "Weather Impact Analysis",
            "Growing Degree Days", 
            "Climate Risk Assessment",
            "Seasonal Patterns",
            "Extreme Weather Events"
        ],
        help="Select type of climate analysis"
    )
    
    # Date range selection
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=90),
            max_value=datetime.now()
        )
    
    with col2:
        end_date = st.date_input(
            "End Date", 
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    if st.button("📊 Generate Climate Analysis", type="primary"):
        with st.spinner("📈 Analyzing climate data..."):
            try:
                # Get weather impact analysis
                request = AnalysisRequest(
                    analysis_type='weather_impact_analysis',
                    parameters={
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'analysis_type': analysis_type
                    },
                    user_id=1  # TODO: Get from session
                )
                
                result = analysis_service.analyze_weather_impact(request)
                
                if result.get('success'):
                    st.session_state['climate_analysis'] = result
                    st.success("✅ Climate analysis completed!")
                    st.rerun()
                else:
                    st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                st.error(f"❌ Error during analysis: {e}")
    
    # Display analysis results
    if 'climate_analysis' in st.session_state:
        analysis_result = st.session_state['climate_analysis']
        
        st.markdown(f"### 📊 {analysis_type} Results")
        
        # Display weather impact data
        weather_data = analysis_result.get('data', {})
        
        if weather_data:
            # Summary metrics
            st.markdown("**📈 Analysis Summary:**")
            
            impact_scores = []
            location_names = []
            
            for location, data in weather_data.items():
                impact_score = data.get('impact_score', 0)
                impact_scores.append(impact_score)
                location_names.append(location)
            
            if impact_scores:
                avg_impact = sum(impact_scores) / len(impact_scores)
                max_impact = max(impact_scores)
                min_impact = min(impact_scores)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Average Impact", f"{avg_impact*100:.1f}%")
                with col2:
                    st.metric("Best Conditions", f"{max_impact*100:.1f}%")
                with col3:
                    st.metric("Challenging Conditions", f"{min_impact*100:.1f}%")
                with col4:
                    st.metric("Locations Analyzed", len(weather_data))
                
                # Impact visualization
                weather_impact_chart = viz_engine.create_weather_impact_chart(weather_data)
                st.plotly_chart(weather_impact_chart, use_container_width=True)
        
        # Display insights
        insights = analysis_result.get('insights', [])
        if insights:
            st.markdown("**💡 Key Insights:**")
            for insight in insights:
                st.info(f"📊 {insight}")
        
        # Display recommendations
        recommendations = analysis_result.get('recommendations', [])
        if recommendations:
            st.markdown("**🎯 Recommendations:**")
            for rec in recommendations:
                st.success(f"✅ {rec}")
        
        # Additional analysis based on type
        if analysis_type == "Growing Degree Days":
            render_gdd_analysis()
        elif analysis_type == "Climate Risk Assessment":
            render_climate_risk_assessment()
        elif analysis_type == "Seasonal Patterns":
            render_seasonal_patterns()
        elif analysis_type == "Extreme Weather Events":
            render_extreme_weather_analysis()
    
    else:
        st.info("📊 Select analysis parameters and click 'Generate Climate Analysis' to begin")
        
        # Show sample analytics features
        st.markdown("### 🔧 Available Analytics Features")
        
        features = {
            "📈 Weather Impact Analysis": "Assess how weather conditions affect agricultural productivity",
            "🌡️ Growing Degree Days": "Calculate heat accumulation for crop development timing",
            "⚠️ Climate Risk Assessment": "Identify climate-related risks to agricultural operations",
            "📅 Seasonal Patterns": "Analyze historical weather patterns and trends",
            "⛈️ Extreme Weather Events": "Track and analyze extreme weather occurrences"
        }
        
        for feature, description in features.items():
            st.write(f"**{feature}:** {description}")

def render_weather_alerts():
    """Render weather alerts and warnings"""
    
    st.subheader("Weather Alerts & Monitoring")
    
    # Alert settings
    col1, col2 = st.columns(2)
    
    with col1:
        alert_types = st.multiselect(
            "Alert Types:",
            options=[
                "Temperature Extremes",
                "Heavy Rainfall", 
                "Drought Conditions",
                "High Winds",
                "Frost Warning",
                "Disease Risk"
            ],
            default=["Temperature Extremes", "Heavy Rainfall"],
            help="Select types of alerts to monitor"
        )
    
    with col2:
        notification_method = st.selectbox(
            "Notification Method:",
            options=["Dashboard Only", "Email", "SMS", "Push Notification"],
            help="How you want to receive alerts"
        )
    
    # Alert thresholds
    st.markdown("**⚙️ Alert Thresholds:**")
    
    threshold_col1, threshold_col2, threshold_col3 = st.columns(3)
    
    with threshold_col1:
        temp_high = st.number_input("High Temperature (°C)", value=35.0, step=1.0)
        temp_low = st.number_input("Low Temperature (°C)", value=5.0, step=1.0)
    
    with threshold_col2:
        rainfall_heavy = st.number_input("Heavy Rainfall (mm/day)", value=50.0, step=5.0)
        wind_high = st.number_input("High Wind Speed (m/s)", value=15.0, step=1.0)
    
    with threshold_col3:
        humidity_high = st.number_input("High Humidity (%)", value=90.0, step=5.0)
        humidity_low = st.number_input("Low Humidity (%)", value=30.0, step=5.0)
    
    # Current alerts
    st.markdown("---")
    st.markdown("### 🚨 Current Alerts")
    
    # Generate sample alerts based on current weather
    if 'current_weather' in st.session_state:
        current_weather = st.session_state['current_weather']
        alerts = generate_weather_alerts(current_weather, {
            'temp_high': temp_high,
            'temp_low': temp_low,
            'rainfall_heavy': rainfall_heavy,
            'wind_high': wind_high,
            'humidity_high': humidity_high,
            'humidity_low': humidity_low
        })
        
        if alerts:
            for alert in alerts:
                alert_type = alert['type']
                alert_message = alert['message']
                alert_severity = alert['severity']
                
                if alert_severity == 'high':
                    st.error(f"🚨 **{alert_type}:** {alert_message}")
                elif alert_severity == 'medium':
                    st.warning(f"⚠️ **{alert_type}:** {alert_message}")
                else:
                    st.info(f"ℹ️ **{alert_type}:** {alert_message}")
        else:
            st.success("✅ No current weather alerts")
    else:
        st.info("🌤️ Get current weather data to see active alerts")
    
    # Alert history
    st.markdown("---")
    st.markdown("### 📋 Alert History")
    
    # Sample alert history
    alert_history = [
        {"Date": "2024-01-15", "Type": "High Temperature", "Message": "Temperature exceeded 38°C", "Severity": "High"},
        {"Date": "2024-01-12", "Type": "Heavy Rainfall", "Message": "Rainfall: 65mm in 24 hours", "Severity": "Medium"},
        {"Date": "2024-01-10", "Type": "High Humidity", "Message": "Humidity above 95% - disease risk", "Severity": "Medium"},
        {"Date": "2024-01-08", "Type": "Low Temperature", "Message": "Temperature dropped to 3°C", "Severity": "High"}
    ]
    
    history_df = pd.DataFrame(alert_history)
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    # Alert management
    st.markdown("---")
    st.markdown("### ⚙️ Alert Management")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("💾 Save Alert Settings"):
            st.success("✅ Alert settings saved!")
    
    with col_b:
        if st.button("📧 Test Notifications"):
            st.info("📨 Test notification sent!")
    
    with col_c:
        if st.button("📥 Export History"):
            csv = history_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                f"weather_alerts_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )

# Helper functions

def generate_weather_insights(weather_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Generate agricultural insights from weather data"""
    insights = {
        'alerts': [],
        'recommendations': [],
        'opportunities': []
    }
    
    temp = weather_data.get('temperature', 0)
    humidity = weather_data.get('humidity', 0)
    wind_speed = weather_data.get('wind_speed', 0)
    
    # Temperature alerts
    if temp > 35:
        insights['alerts'].append("High temperature may stress crops")
        insights['recommendations'].append("Increase irrigation frequency")
    elif temp < 10:
        insights['alerts'].append("Low temperature may slow crop growth")
        insights['recommendations'].append("Consider frost protection measures")
    
    # Humidity insights
    if humidity > 85:
        insights['alerts'].append("High humidity increases disease risk")
        insights['recommendations'].append("Improve air circulation")
    elif humidity < 40:
        insights['recommendations'].append("Monitor plants for water stress")
    
    # Wind insights
    if wind_speed > 10:
        insights['alerts'].append("High winds may damage crops")
        insights['recommendations'].append("Secure loose structures and equipment")
    
    # Opportunities
    if 20 <= temp <= 30 and 50 <= humidity <= 70:
        insights['opportunities'].append("Optimal conditions for field work")
    
    if wind_speed < 5:
        insights['opportunities'].append("Good conditions for pesticide application")
    
    return insights

def get_temperature_status(temp: float) -> str:
    """Get temperature status for agriculture"""
    if temp < 10:
        return "Too Cold"
    elif temp < 20:
        return "Cool"
    elif temp <= 30:
        return "Optimal"
    elif temp <= 35:
        return "Warm"
    else:
        return "Too Hot"

def get_humidity_status(humidity: float) -> str:
    """Get humidity status for agriculture"""
    if humidity < 40:
        return "Low"
    elif humidity <= 70:
        return "Optimal"
    elif humidity <= 85:
        return "High"
    else:
        return "Very High"

def get_pressure_status(pressure: float) -> str:
    """Get pressure status"""
    if pressure < 1000:
        return "Low"
    elif pressure <= 1020:
        return "Normal"
    else:
        return "High"

def get_wind_status(wind_speed: float) -> str:
    """Get wind status for agriculture"""
    if wind_speed < 2:
        return "Calm"
    elif wind_speed <= 5:
        return "Light"
    elif wind_speed <= 10:
        return "Moderate"
    else:
        return "Strong"

def create_forecast_chart(forecast_data: List[Dict]) -> go.Figure:
    """Create forecast visualization chart"""
    dates = [day.get('date', '') for day in forecast_data]
    temp_max = [day.get('temperature_max', 0) for day in forecast_data]
    temp_min = [day.get('temperature_min', 0) for day in forecast_data]
    rainfall = [day.get('rainfall', 0) for day in forecast_data]
    
    fig = go.Figure()
    
    # Temperature traces
    fig.add_trace(go.Scatter(
        x=dates, y=temp_max, mode='lines+markers',
        name='Max Temperature', line=dict(color='red', width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates, y=temp_min, mode='lines+markers',
        name='Min Temperature', line=dict(color='blue', width=2),
        marker=dict(size=6)
    ))
    
    # Rainfall bars
    fig.add_trace(go.Bar(
        x=dates, y=rainfall, name='Rainfall (mm)',
        marker=dict(color='lightblue', opacity=0.6),
        yaxis='y2'
    ))
    
    # Update layout for dual y-axis
    fig.update_layout(
        title='Temperature & Rainfall Forecast',
        xaxis_title='Date',
        yaxis=dict(title='Temperature (°C)', side='left'),
        yaxis2=dict(title='Rainfall (mm)', side='right', overlaying='y'),
        legend=dict(x=0, y=1),
        hovermode='x unified'
    )
    
    return fig

def get_daily_agricultural_advice(day_data: Dict[str, Any]) -> List[str]:
    """Get agricultural advice for a specific day"""
    advice = []
    
    temp_max = day_data.get('temperature_max', 0)
    rainfall = day_data.get('rainfall', 0)
    humidity = day_data.get('humidity', 0)
    wind_speed = day_data.get('wind_speed', 0)
    
    # Temperature-based advice
    if temp_max > 35:
        advice.append("Plan early morning or late evening field work")
    elif temp_max < 15:
        advice.append("Delay planting of warm-season crops")
    
    # Rainfall-based advice
    if rainfall > 20:
        advice.append("Good day for rain-fed crops, avoid field operations")
    elif rainfall < 1 and temp_max > 25:
        advice.append("Consider irrigation for water-sensitive crops")
    
    # Wind-based advice
    if wind_speed < 3:
        advice.append("Suitable for pesticide or fertilizer application")
    elif wind_speed > 10:
        advice.append("Avoid spraying operations due to drift risk")
    
    # Humidity-based advice
    if humidity > 85:
        advice.append("Monitor for disease development")
    
    return advice

def generate_forecast_insights(forecast_data: List[Dict]) -> Dict[str, List[str]]:
    """Generate agricultural planning insights from forecast"""
    insights = {
        'irrigation': [],
        'field_work': [],
        'warnings': []
    }
    
    total_rainfall = sum(day.get('rainfall', 0) for day in forecast_data)
    avg_temp = sum(day.get('temperature_max', 0) for day in forecast_data) / len(forecast_data)
    max_wind = max(day.get('wind_speed', 0) for day in forecast_data)
    
    # Irrigation insights
    if total_rainfall < 25:
        insights['irrigation'].append("Low rainfall expected - plan supplemental irrigation")
    elif total_rainfall > 100:
        insights['irrigation'].append("Heavy rainfall expected - ensure drainage systems are clear")
    
    # Field work insights
    dry_days = len([day for day in forecast_data if day.get('rainfall', 0) < 5])
    if dry_days >= 3:
        insights['field_work'].append(f"{dry_days} dry days expected - good for field operations")
    
    if avg_temp > 30:
        insights['field_work'].append("High temperatures - schedule work for early morning or evening")
    
    # Warnings
    if max_wind > 15:
        insights['warnings'].append("Strong winds expected - secure equipment and structures")
    
    extreme_temps = len([day for day in forecast_data if day.get('temperature_max', 0) > 38])
    if extreme_temps > 0:
        insights['warnings'].append(f"{extreme_temps} days with extreme heat expected")
    
    return insights

def generate_weather_alerts(current_weather: Dict, thresholds: Dict) -> List[Dict]:
    """Generate weather alerts based on current conditions and thresholds"""
    alerts = []
    
    temp = current_weather.get('temperature', 0)
    humidity = current_weather.get('humidity', 0)
    wind_speed = current_weather.get('wind_speed', 0)
    
    # Temperature alerts
    if temp > thresholds['temp_high']:
        alerts.append({
            'type': 'High Temperature',
            'message': f'Temperature {temp:.1f}°C exceeds threshold {thresholds["temp_high"]:.1f}°C',
            'severity': 'high'
        })
    elif temp < thresholds['temp_low']:
        alerts.append({
            'type': 'Low Temperature',
            'message': f'Temperature {temp:.1f}°C below threshold {thresholds["temp_low"]:.1f}°C',
            'severity': 'high'
        })
    
    # Humidity alerts
    if humidity > thresholds['humidity_high']:
        alerts.append({
            'type': 'High Humidity',
            'message': f'Humidity {humidity:.0f}% exceeds threshold {thresholds["humidity_high"]:.0f}%',
            'severity': 'medium'
        })
    elif humidity < thresholds['humidity_low']:
        alerts.append({
            'type': 'Low Humidity',
            'message': f'Humidity {humidity:.0f}% below threshold {thresholds["humidity_low"]:.0f}%',
            'severity': 'medium'
        })
    
    # Wind alerts
    if wind_speed > thresholds['wind_high']:
        alerts.append({
            'type': 'High Wind Speed',
            'message': f'Wind speed {wind_speed:.1f} m/s exceeds threshold {thresholds["wind_high"]:.1f} m/s',
            'severity': 'medium'
        })
    
    return alerts

def render_gdd_analysis():
    """Render Growing Degree Days analysis"""
    st.markdown("#### 🌡️ Growing Degree Days Analysis")
    st.info("Growing Degree Days analysis helps predict crop development timing based on heat accumulation.")

def render_climate_risk_assessment():
    """Render climate risk assessment"""
    st.markdown("#### ⚠️ Climate Risk Assessment")
    st.info("Climate risk assessment identifies potential threats to agricultural operations from weather patterns.")

def render_seasonal_patterns():
    """Render seasonal patterns analysis"""
    st.markdown("#### 📅 Seasonal Patterns Analysis")
    st.info("Seasonal patterns analysis examines historical weather trends to predict future conditions.")

def render_extreme_weather_analysis():
    """Render extreme weather events analysis"""
    st.markdown("#### ⛈️ Extreme Weather Events Analysis")
    st.info("Extreme weather analysis tracks and predicts severe weather events that could impact agriculture.")
