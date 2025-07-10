import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_processing import generate_soil_sample_data
from config.translator import translate_text


st.set_page_config(page_title="Soil Monitoring", page_icon="🌱", layout="wide")

st.title("🌱 Soil Monitoring & Analysis")
st.markdown("### Comprehensive soil condition monitoring and analysis")

# Initialize soil data if not exists
if 'soil_data' not in st.session_state:
    st.session_state.soil_data = generate_soil_sample_data()

# Sidebar for monitoring settings
st.sidebar.title("Monitoring Settings")

# Field selection
field_id = st.sidebar.selectbox(
    "Select Field",
    ["Field_1", "Field_2", "Field_3", "Field_4", "Field_5"],
    help="Choose field for detailed analysis"
)

# Time range for analysis
time_range = st.sidebar.selectbox(
    "Analysis Period",
    ["Last 7 days", "Last 30 days", "Last 90 days", "Last year"],
    index=1
)

# Refresh data button
if st.sidebar.button("🔄 Refresh Soil Data"):
    st.session_state.soil_data = generate_soil_sample_data()
    st.rerun()

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Current Status", "Nutrient Analysis", "pH Monitoring", "Moisture Tracking", "Recommendations"])

with tab1:
    st.subheader("Current Soil Status")

    # Get current soil data for selected field
    soil_data = st.session_state.soil_data
    current_data = soil_data[soil_data['field_id'] == field_id].iloc[-1] if len(soil_data) > 0 else {}

    if current_data is not None and not current_data.empty:
        # Key soil metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ph_value = current_data.get('ph', 0)
            ph_status = "Optimal" if 6.0 <= ph_value <= 7.5 else "Attention Needed"
            ph_delta = ph_value - 6.5  # Optimal pH

            st.metric(
                "Soil pH",
                f"{ph_value:.1f}",
                delta=f"{ph_delta:+.1f} from optimal",
                help="Soil pH level (6.0-7.5 optimal for most crops)"
            )

        with col2:
            moisture = current_data.get('moisture', 0)
            moisture_status = "Good" if 40 <= moisture <= 70 else "Monitor"

            st.metric(
                "Moisture Content",
                f"{moisture:.1f}%",
                help="Soil moisture percentage"
            )

        with col3:
            temperature = current_data.get('temperature', 0)
            st.metric(
                "Soil Temperature",
                f"{temperature:.1f}°C",
                help="Current soil temperature"
            )

        with col4:
            conductivity = current_data.get('conductivity', 0)
            st.metric(
                "Electrical Conductivity",
                f"{conductivity:.2f} dS/m",
                help="Soil electrical conductivity (salinity indicator)"
            )

        # Soil health summary
        st.markdown("---")
        st.subheader("Soil Health Summary")

        col1, col2 = st.columns(2)

        with col1:
            # Health indicators
            indicators = []

            # pH assessment
            if 6.0 <= ph_value <= 7.5:
                indicators.append(("pH Level", "✅ Optimal", "green"))
            elif 5.5 <= ph_value < 6.0 or 7.5 < ph_value <= 8.0:
                indicators.append(("pH Level", "⚠️ Moderate", "orange"))
            else:
                indicators.append(("pH Level", "❌ Poor", "red"))

            # Moisture assessment
            if 40 <= moisture <= 70:
                indicators.append(("Moisture", "✅ Good", "green"))
            elif 30 <= moisture < 40 or 70 < moisture <= 80:
                indicators.append(("Moisture", "⚠️ Monitor", "orange"))
            else:
                indicators.append(("Moisture", "❌ Critical", "red"))

            # Temperature assessment
            if 15 <= temperature <= 25:
                indicators.append(("Temperature", "✅ Optimal", "green"))
            elif 10 <= temperature < 15 or 25 < temperature <= 30:
                indicators.append(("Temperature", "⚠️ Acceptable", "orange"))
            else:
                indicators.append(("Temperature", "❌ Extreme", "red"))

            for indicator, status, color in indicators:
                st.markdown(f"**{indicator}:** {status}")

        with col2:
            # Overall health score
            health_scores = []
            if 6.0 <= ph_value <= 7.5:
                health_scores.append(100)
            elif 5.5 <= ph_value < 6.0 or 7.5 < ph_value <= 8.0:
                health_scores.append(70)
            else:
                health_scores.append(30)

            if 40 <= moisture <= 70:
                health_scores.append(100)
            elif 30 <= moisture < 40 or 70 < moisture <= 80:
                health_scores.append(70)
            else:
                health_scores.append(30)

            overall_health = np.mean(health_scores)

            # Create gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = overall_health,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Overall Soil Health"},
                delta = {'reference': 80},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

    else:
        st.error("No current soil data available for the selected field.")

with tab2:
    st.subheader("Nutrient Analysis")

    # Nutrient level monitoring
    nutrients = ['nitrogen', 'phosphorus', 'potassium', 'organic_matter']

    if len(soil_data) > 0:
        field_data = soil_data[soil_data['field_id'] == field_id]

        if len(field_data) > 0:
            # Current nutrient levels
            latest_data = field_data.iloc[-1]

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                nitrogen = latest_data.get('nitrogen', 0)
                n_status = "Good" if 20 <= nitrogen <= 50 else "Monitor"
                st.metric(
                    "Nitrogen (N)",
                    f"{nitrogen:.1f} ppm",
                    help="Nitrogen content in soil"
                )

            with col2:
                phosphorus = latest_data.get('phosphorus', 0)
                p_status = "Good" if 15 <= phosphorus <= 40 else "Monitor"
                st.metric(
                    "Phosphorus (P)",
                    f"{phosphorus:.1f} ppm",
                    help="Phosphorus content in soil"
                )

            with col3:
                potassium = latest_data.get('potassium', 0)
                k_status = "Good" if 100 <= potassium <= 300 else "Monitor"
                st.metric(
                    "Potassium (K)",
                    f"{potassium:.1f} ppm",
                    help="Potassium content in soil"
                )

            with col4:
                organic_matter = latest_data.get('organic_matter', 0)
                om_status = "Good" if organic_matter >= 3.0 else "Low"
                st.metric(
                    "Organic Matter",
                    f"{organic_matter:.1f}%",
                    help="Organic matter percentage"
                )

            # Nutrient trends
            st.markdown("**Nutrient Trends Over Time**")

            if len(field_data) > 1:
                # Line chart for nutrient trends
                fig_nutrients = go.Figure()

                for nutrient in nutrients:
                    if nutrient in field_data.columns:
                        fig_nutrients.add_trace(go.Scatter(
                            x=field_data['date'],
                            y=field_data[nutrient],
                            mode='lines+markers',
                            name=nutrient.title()
                        ))

                fig_nutrients.update_layout(
                    title="Nutrient Level Trends",
                    xaxis_title="Date",
                    yaxis_title="Concentration",
                    height=400
                )
                st.plotly_chart(fig_nutrients, use_container_width=True)

            # Nutrient balance analysis
            st.markdown("**Nutrient Balance Analysis**")

            # NPK ratio analysis
            n_val = latest_data.get('nitrogen', 0)
            p_val = latest_data.get('phosphorus', 0)
            k_val = latest_data.get('potassium', 0)

            if n_val > 0 and p_val > 0 and k_val > 0:
                # Calculate ratios (simplified)
                total_npk = n_val + p_val + k_val
                n_ratio = (n_val / total_npk) * 100
                p_ratio = (p_val / total_npk) * 100
                k_ratio = (k_val / total_npk) * 100

                fig_pie = px.pie(
                    values=[n_ratio, p_ratio, k_ratio],
                    names=['Nitrogen', 'Phosphorus', 'Potassium'],
                    title="NPK Distribution"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        else:
            st.warning("No nutrient data available for the selected field.")
    else:
        st.error("No soil data available.")

with tab3:
    st.subheader("pH Monitoring")

    if len(soil_data) > 0:
        field_data = soil_data[soil_data['field_id'] == field_id]

        if len(field_data) > 0 and 'ph' in field_data.columns:
            # pH trend chart
            fig_ph = go.Figure()

            fig_ph.add_trace(go.Scatter(
                x=field_data['date'],
                y=field_data['ph'],
                mode='lines+markers',
                name='pH Level',
                line=dict(color='blue')
            ))

            # Add optimal pH range
            fig_ph.add_hline(y=6.0, line_dash="dash", line_color="green",
                           annotation_text="Optimal Min (6.0)")
            fig_ph.add_hline(y=7.5, line_dash="dash", line_color="green",
                           annotation_text="Optimal Max (7.5)")

            fig_ph.update_layout(
                title="Soil pH Trend",
                xaxis_title="Date",
                yaxis_title="pH Level",
                height=400,
                yaxis=dict(range=[4, 10])
            )
            st.plotly_chart(fig_ph, use_container_width=True)

            # pH analysis
            col1, col2 = st.columns(2)

            with col1:
                current_ph = field_data['ph'].iloc[-1]
                avg_ph = field_data['ph'].mean()
                ph_std = field_data['ph'].std()

                st.markdown("**pH Statistics**")
                st.write(f"Current pH: {current_ph:.2f}")
                st.write(f"Average pH: {avg_ph:.2f}")
                st.write(f"pH Variability: ±{ph_std:.2f}")

                # pH classification
                if current_ph < 5.5:
                    ph_class = "Strongly Acidic"
                    ph_color = "red"
                elif current_ph < 6.0:
                    ph_class = "Moderately Acidic"
                    ph_color = "orange"
                elif current_ph <= 7.5:
                    ph_class = "Optimal"
                    ph_color = "green"
                elif current_ph <= 8.0:
                    ph_class = "Slightly Alkaline"
                    ph_color = "orange"
                else:
                    ph_class = "Strongly Alkaline"
                    ph_color = "red"

                st.markdown(f"**pH Classification:** :{ph_color}[{ph_class}]")

            with col2:
                st.markdown("**pH Management Recommendations**")

                if current_ph < 6.0:
                    st.write("🟡 **Acidic Soil Management:**")
                    st.write("• Apply lime to raise pH")
                    st.write("• Use calcium carbonate or dolomite")
                    st.write("• Consider organic matter addition")
                elif current_ph > 7.5:
                    st.write("🔵 **Alkaline Soil Management:**")
                    st.write("• Apply sulfur to lower pH")
                    st.write("• Use acidifying fertilizers")
                    st.write("• Add organic acids")
                else:
                    st.write("🟢 **pH is in optimal range:**")
                    st.write("• Maintain current practices")
                    st.write("• Monitor regularly")
                    st.write("• Consider crop-specific adjustments")

        else:
            st.warning("No pH data available for the selected field.")

with tab4:
    st.subheader("Moisture Tracking")

    if len(soil_data) > 0:
        field_data = soil_data[soil_data['field_id'] == field_id]

        if len(field_data) > 0 and 'moisture' in field_data.columns:
            # Moisture trend chart
            fig_moisture = go.Figure()

            fig_moisture.add_trace(go.Scatter(
                x=field_data['date'],
                y=field_data['moisture'],
                mode='lines+markers',
                name='Soil Moisture',
                line=dict(color='blue'),
                fill='tozeroy',
                fillcolor='rgba(0,100,80,0.2)'
            ))

            # Add optimal moisture range
            fig_moisture.add_hline(y=40, line_dash="dash", line_color="green",
                                 annotation_text="Optimal Min (40%)")
            fig_moisture.add_hline(y=70, line_dash="dash", line_color="green",
                                 annotation_text="Optimal Max (70%)")

            fig_moisture.update_layout(
                title="Soil Moisture Trend",
                xaxis_title="Date",
                yaxis_title="Moisture Content (%)",
                height=400,
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig_moisture, use_container_width=True)

            # Moisture analysis
            col1, col2 = st.columns(2)

            with col1:
                current_moisture = field_data['moisture'].iloc[-1]
                avg_moisture = field_data['moisture'].mean()
                moisture_trend = field_data['moisture'].iloc[-3:].mean() - field_data['moisture'].iloc[-6:-3].mean()

                st.markdown("**Moisture Statistics**")
                st.write(f"Current Moisture: {current_moisture:.1f}%")
                st.write(f"Average Moisture: {avg_moisture:.1f}%")
                st.write(f"Recent Trend: {moisture_trend:+.1f}%")

                # Moisture status
                if current_moisture < 30:
                    moisture_status = "Critically Low"
                    moisture_color = "red"
                elif current_moisture < 40:
                    moisture_status = "Low"
                    moisture_color = "orange"
                elif current_moisture <= 70:
                    moisture_status = "Optimal"
                    moisture_color = "green"
                elif current_moisture <= 80:
                    moisture_status = "High"
                    moisture_color = "orange"
                else:
                    moisture_status = "Excessive"
                    moisture_color = "red"

                st.markdown(f"**Moisture Status:** :{moisture_color}[{moisture_status}]")

            with col2:
                st.markdown("**Irrigation Recommendations**")

                if current_moisture < 40:
                    st.write("💧 **Irrigation Needed:**")
                    st.write("• Increase watering frequency")
                    st.write("• Check irrigation system")
                    st.write("• Consider mulching")
                elif current_moisture > 70:
                    st.write("⚠️ **Reduce Irrigation:**")
                    st.write("• Decrease watering frequency")
                    st.write("• Improve drainage")
                    st.write("• Monitor for root rot")
                else:
                    st.write("✅ **Moisture is optimal:**")
                    st.write("• Maintain current irrigation")
                    st.write("• Monitor weather conditions")
                    st.write("• Adjust based on crop needs")

        else:
            st.warning("No moisture data available for the selected field.")

with tab5:
    st.subheader("Soil Management Recommendations")

    if len(soil_data) > 0:
        field_data = soil_data[soil_data['field_id'] == field_id]

        if len(field_data) > 0:
            latest_data = field_data.iloc[-1]

            # Comprehensive recommendations
            st.markdown("**Immediate Actions Required:**")

            immediate_actions = []

            # pH recommendations
            ph = latest_data.get('ph', 7.0)
            if ph < 6.0:
                immediate_actions.append("🟡 Apply lime to correct soil acidity")
            elif ph > 8.0:
                immediate_actions.append("🔵 Apply sulfur to reduce soil alkalinity")

            # Moisture recommendations
            moisture = latest_data.get('moisture', 50)
            if moisture < 30:
                immediate_actions.append("💧 Urgent irrigation required")
            elif moisture > 80:
                immediate_actions.append("🚰 Improve field drainage")

            # Nutrient recommendations
            nitrogen = latest_data.get('nitrogen', 30)
            if nitrogen < 20:
                immediate_actions.append("🌱 Apply nitrogen fertilizer")

            phosphorus = latest_data.get('phosphorus', 25)
            if phosphorus < 15:
                immediate_actions.append("🧬 Supplement phosphorus levels")

            if not immediate_actions:
                st.success("✅ No immediate actions required - soil conditions are good!")
            else:
                for action in immediate_actions:
                    st.write(action)

            # Long-term recommendations
            st.markdown("---")
            st.markdown("**Long-term Soil Health Strategy:**")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Soil Improvement Plan:**")
                st.write("• Regular organic matter addition")
                st.write("• Crop rotation implementation")
                st.write("• Cover crop utilization")
                st.write("• Precision fertilizer application")
                st.write("• Soil testing every 6 months")

            with col2:
                st.markdown("**Monitoring Schedule:**")
                st.write("• Daily: Moisture levels")
                st.write("• Weekly: pH monitoring")
                st.write("• Monthly: Nutrient analysis")
                st.write("• Seasonal: Comprehensive soil test")
                st.write("• Annual: Soil health assessment")

            # Crop-specific recommendations
            st.markdown("---")
            st.subheader("Crop-Specific Soil Requirements")

            crop_selection = st.selectbox(
                "Select Crop for Specific Recommendations",
                ["Wheat", "Corn", "Rice", "Soybeans", "Tomatoes", "Potatoes"]
            )

            crop_requirements = {
                "Wheat": {
                    "ph_range": "6.0-7.5",
                    "nitrogen": "40-60 ppm",
                    "moisture": "45-65%",
                    "special": "Good drainage, moderate fertility"
                },
                "Corn": {
                    "ph_range": "6.0-7.0",
                    "nitrogen": "50-80 ppm",
                    "moisture": "50-70%",
                    "special": "High nitrogen demand, deep soil preferred"
                },
                "Rice": {
                    "ph_range": "5.5-7.0",
                    "nitrogen": "30-50 ppm",
                    "moisture": "80-100% (flooded)",
                    "special": "Flooded conditions, clayey soil preferred"
                },
                "Soybeans": {
                    "ph_range": "6.0-7.0",
                    "nitrogen": "20-40 ppm",
                    "moisture": "45-65%",
                    "special": "Nitrogen-fixing, good drainage needed"
                },
                "Tomatoes": {
                    "ph_range": "6.0-7.0",
                    "nitrogen": "40-60 ppm",
                    "moisture": "55-75%",
                    "special": "Consistent moisture, high organic matter"
                },
                "Potatoes": {
                    "ph_range": "5.8-6.5",
                    "nitrogen": "35-55 ppm",
                    "moisture": "50-70%",
                    "special": "Slightly acidic, loose soil texture"
                }
            }

            if crop_selection in crop_requirements:
                req = crop_requirements[crop_selection]

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**{crop_selection} Requirements:**")
                    st.write(f"• pH Range: {req['ph_range']}")
                    st.write(f"• Nitrogen: {req['nitrogen']}")
                    st.write(f"• Moisture: {req['moisture']}")
                    st.write(f"• Special: {req['special']}")

                with col2:
                    st.markdown("**Compatibility Assessment:**")

                    # Check compatibility with current soil conditions
                    compatibility_score = 0
                    total_checks = 0

                    # pH compatibility
                    current_ph = latest_data.get('ph', 7.0)
                    ph_range = req['ph_range'].split('-')
                    if len(ph_range) == 2:
                        ph_min, ph_max = float(ph_range[0]), float(ph_range[1])
                        if ph_min <= current_ph <= ph_max:
                            st.write("✅ pH Compatible")
                            compatibility_score += 1
                        else:
                            st.write("❌ pH Needs Adjustment")
                        total_checks += 1

                    # Nitrogen compatibility
                    current_n = latest_data.get('nitrogen', 30)
                    n_range = req['nitrogen'].split('-')
                    if len(n_range) == 2:
                        n_min, n_max = float(n_range[0].split()[0]), float(n_range[1].split()[0])
                        if n_min <= current_n <= n_max:
                            st.write("✅ Nitrogen Adequate")
                            compatibility_score += 1
                        else:
                            st.write("❌ Nitrogen Adjustment Needed")
                        total_checks += 1

                    if total_checks > 0:
                        compatibility_percent = (compatibility_score / total_checks) * 100
                        st.write(f"**Overall Compatibility: {compatibility_percent:.0f}%**")

        else:
            st.warning("No soil data available for recommendations.")
    else:
        st.error("No soil monitoring data available.")
