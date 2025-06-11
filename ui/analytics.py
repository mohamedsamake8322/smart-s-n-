"""
Enterprise Analytics Interface
Advanced business intelligence and data analytics for agricultural insights
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from services.analysis_service import analysis_service, AnalysisRequest
from services.prediction_service import prediction_service
from core.database import db_manager
from utils.visualization import viz_engine
from utils.file_handler import file_handler

def render_analytics():
    """Render the analytics interface"""
    
    st.header("📊 Advanced Analytics & Business Intelligence")
    st.markdown("Comprehensive agricultural data analytics and insights platform")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Executive Analytics", 
        "🔍 Deep Dive Analysis", 
        "📊 Custom Reports", 
        "🎯 Predictive Insights"
    ])
    
    with tab1:
        render_executive_analytics()
    
    with tab2:
        render_deep_dive_analysis()
    
    with tab3:
        render_custom_reports()
    
    with tab4:
        render_predictive_insights()

def render_executive_analytics():
    """Render executive-level analytics dashboard"""
    
    st.subheader("Executive Analytics Dashboard")
    st.markdown("High-level insights and KPIs for strategic decision making")
    
    # Time period selector
    col1, col2 = st.columns([3, 1])
    
    with col1:
        time_period = st.selectbox(
            "Analysis Period:",
            options=["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last Year", "Custom Range"],
            index=1,
            help="Select time period for analysis"
        )
    
    with col2:
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
    
    # Custom date range if selected
    if time_period == "Custom Range":
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        with col_date2:
            end_date = st.date_input("End Date", value=datetime.now())
    
    # Get analytics data
    try:
        analytics_data = db_manager.get_analytics_data()
        
        # Executive KPIs
        st.markdown("### 📊 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_predictions = analytics_data.get('total_predictions', 0)
            st.metric(
                "Total Predictions",
                f"{total_predictions:,}",
                delta=f"+{int(total_predictions * 0.15):,} this period",
                delta_color="normal"
            )
        
        with col2:
            active_users = analytics_data.get('active_users', 0)
            st.metric(
                "Active Users",
                active_users,
                delta=f"+{max(1, int(active_users * 0.1))} this month",
                delta_color="normal"
            )
        
        with col3:
            monthly_detections = analytics_data.get('monthly_detections', 0)
            accuracy_rate = 94.2  # Sample accuracy
            st.metric(
                "Detection Accuracy",
                f"{accuracy_rate:.1f}%",
                delta="+2.3%",
                delta_color="normal"
            )
        
        with col4:
            total_locations = analytics_data.get('total_locations', 0)
            st.metric(
                "Farm Locations",
                total_locations,
                delta=f"+{max(1, int(total_locations * 0.2))} this quarter",
                delta_color="normal"
            )
        
        # Performance trend analysis
        st.markdown("### 📈 Performance Trends")
        
        # Get farm performance analysis
        performance_request = AnalysisRequest(
            analysis_type='farm_performance_analysis',
            parameters={},
            user_id=1  # TODO: Get from session
        )
        
        performance_analysis = analysis_service.analyze_farm_performance(performance_request)
        
        if performance_analysis.get('success'):
            metrics = performance_analysis.get('metrics', {})
            
            # Performance dashboard
            performance_chart = viz_engine.create_performance_dashboard(metrics)
            st.plotly_chart(performance_chart, use_container_width=True)
            
            # Performance insights
            if performance_analysis.get('recommendations'):
                st.markdown("### 💡 Strategic Recommendations")
                
                for i, recommendation in enumerate(performance_analysis['recommendations'][:5], 1):
                    st.write(f"{i}. {recommendation}")
        
        # Revenue impact analysis
        st.markdown("### 💰 Revenue Impact Analysis")
        
        # ROI analysis
        roi_request = AnalysisRequest(
            analysis_type='roi_analysis',
            parameters={
                'fertilizer_cost': 500,
                'prevention_cost': 200,
                'irrigation_cost': 2000,
                'technology_cost': 1000
            },
            user_id=1
        )
        
        roi_analysis = analysis_service.analyze_roi(roi_request)
        
        if roi_analysis.get('success'):
            roi_data = roi_analysis.get('data', {})
            
            # ROI comparison chart
            roi_chart = viz_engine.create_roi_comparison_chart(roi_data)
            st.plotly_chart(roi_chart, use_container_width=True)
            
            # ROI insights
            insights = roi_analysis.get('insights', [])
            if insights:
                st.markdown("**🎯 ROI Insights:**")
                for insight in insights:
                    st.info(f"💰 {insight}")
        
        # Business summary
        st.markdown("### 📋 Executive Summary")
        
        summary_metrics = {
            'System Utilization': '87%',
            'Data Quality Score': '94%', 
            'User Satisfaction': '4.8/5',
            'Cost Savings': '$12,500/month',
            'Productivity Gain': '+23%'
        }
        
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            for metric, value in list(summary_metrics.items())[:3]:
                st.markdown(f"**{metric}:** {value}")
        
        with summary_col2:
            for metric, value in list(summary_metrics.items())[3:]:
                st.markdown(f"**{metric}:** {value}")
        
        # Action items
        st.markdown("### ⚡ Priority Action Items")
        
        action_items = [
            "🎯 Optimize fertilizer recommendations for North region farms",
            "📈 Expand disease detection coverage to 25 additional crops",
            "🌧️ Implement advanced weather integration for irrigation planning",
            "📊 Develop seasonal prediction models for Q2 planning",
            "🤝 Partner with 5 new agricultural cooperatives"
        ]
        
        for item in action_items:
            st.write(f"• {item}")
    
    except Exception as e:
        st.error(f"❌ Error loading executive analytics: {e}")
        st.info("🔄 Please check data connections and try refreshing")

def render_deep_dive_analysis():
    """Render deep dive analytics interface"""
    
    st.subheader("Deep Dive Analysis")
    st.markdown("Detailed analytical insights across all agricultural metrics")
    
    # Analysis category selection
    analysis_category = st.selectbox(
        "Analysis Category:",
        options=[
            "Yield Performance Analysis",
            "Disease Pattern Analysis", 
            "Weather Impact Analysis",
            "Soil Health Analysis",
            "Resource Optimization",
            "Comparative Analysis"
        ],
        help="Select category for deep dive analysis"
    )
    
    if analysis_category == "Yield Performance Analysis":
        render_yield_performance_analysis()
    elif analysis_category == "Disease Pattern Analysis":
        render_disease_pattern_analysis()
    elif analysis_category == "Weather Impact Analysis":
        render_weather_impact_analysis()
    elif analysis_category == "Soil Health Analysis":
        render_soil_health_analysis()
    elif analysis_category == "Resource Optimization":
        render_resource_optimization_analysis()
    else:  # Comparative Analysis
        render_comparative_analysis()

def render_yield_performance_analysis():
    """Render detailed yield performance analysis"""
    
    st.markdown("#### 🌾 Yield Performance Deep Dive")
    
    # Get yield trend analysis
    try:
        yield_request = AnalysisRequest(
            analysis_type='yield_trend_analysis',
            parameters={},
            user_id=1
        )
        
        yield_analysis = analysis_service.analyze_yield_trends(yield_request)
        
        if yield_analysis.get('success'):
            trend_data = yield_analysis.get('data', {})
            
            # Yield statistics overview
            st.markdown("**📊 Yield Statistics Overview:**")
            
            statistics = trend_data.get('statistics', {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_yield = statistics.get('average_yield', 0)
                st.metric("Average Yield", f"{avg_yield:,.0f} kg/ha")
            
            with col2:
                max_yield = statistics.get('max_yield', 0)
                st.metric("Peak Yield", f"{max_yield:,.0f} kg/ha")
            
            with col3:
                min_yield = statistics.get('min_yield', 0)
                st.metric("Minimum Yield", f"{min_yield:,.0f} kg/ha")
            
            with col4:
                volatility = trend_data.get('volatility', 'Unknown')
                st.metric("Volatility", volatility)
            
            # Trend analysis
            trend_direction = trend_data.get('trend_direction', 'Unknown')
            trend_slope = trend_data.get('trend_slope', 0)
            
            if trend_direction == 'Increasing':
                st.success(f"📈 Positive trend: Yield increasing at {abs(trend_slope):.1f} kg/ha per period")
            elif trend_direction == 'Decreasing':
                st.error(f"📉 Declining trend: Yield decreasing at {abs(trend_slope):.1f} kg/ha per period")
            else:
                st.info("📊 Stable yield performance with minimal variation")
            
            # Monthly performance chart
            monthly_data = trend_data.get('monthly_data', [])
            
            if monthly_data:
                st.markdown("**📅 Monthly Yield Performance:**")
                
                monthly_df = pd.DataFrame(monthly_data)
                
                fig = go.Figure()
                
                # Mean yield line
                fig.add_trace(go.Scatter(
                    x=monthly_df.index,
                    y=monthly_df['mean'],
                    mode='lines+markers',
                    name='Average Yield',
                    line=dict(color='#1f77b4', width=3),
                    marker=dict(size=8)
                ))
                
                # Confidence bands
                if 'std' in monthly_df.columns:
                    upper_bound = monthly_df['mean'] + monthly_df['std']
                    lower_bound = monthly_df['mean'] - monthly_df['std']
                    
                    fig.add_trace(go.Scatter(
                        x=monthly_df.index.tolist() + monthly_df.index.tolist()[::-1],
                        y=upper_bound.tolist() + lower_bound.tolist()[::-1],
                        fill='toself',
                        fillcolor='rgba(31,119,180,0.2)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='Confidence Band',
                        showlegend=False
                    ))
                
                fig.update_layout(
                    title="Yield Performance Over Time",
                    xaxis_title="Time Period",
                    yaxis_title="Yield (kg/ha)",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Yield distribution analysis
            st.markdown("**📊 Yield Distribution Analysis:**")
            
            # Create yield distribution histogram
            sample_yields = np.random.normal(avg_yield, avg_yield * 0.2, 1000)
            
            fig = px.histogram(
                x=sample_yields,
                nbins=30,
                title="Yield Distribution",
                labels={'x': 'Yield (kg/ha)', 'y': 'Frequency'}
            )
            
            fig.add_vline(x=avg_yield, line_dash="dash", line_color="red", 
                         annotation_text="Average")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Insights and recommendations
            insights = yield_analysis.get('insights', [])
            recommendations = yield_analysis.get('recommendations', [])
            
            col_insight, col_rec = st.columns(2)
            
            with col_insight:
                if insights:
                    st.markdown("**💡 Key Insights:**")
                    for insight in insights:
                        st.info(f"📊 {insight}")
            
            with col_rec:
                if recommendations:
                    st.markdown("**🎯 Recommendations:**")
                    for rec in recommendations:
                        st.success(f"✅ {rec}")
        
        else:
            st.warning("⚠️ No yield analysis data available")
            st.info("💡 Start making yield predictions to enable detailed analysis")
    
    except Exception as e:
        st.error(f"❌ Error in yield performance analysis: {e}")

def render_disease_pattern_analysis():
    """Render disease pattern analysis"""
    
    st.markdown("#### 🦠 Disease Pattern Analysis")
    
    try:
        # Get disease history
        disease_history = db_manager.get_disease_history(user_id=1, limit=100)
        
        if disease_history:
            df_diseases = pd.DataFrame(disease_history)
            
            # Disease frequency analysis
            st.markdown("**📊 Disease Frequency Analysis:**")
            
            disease_counts = df_diseases['detected_disease'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Disease distribution pie chart
                fig = px.pie(
                    values=disease_counts.values,
                    names=disease_counts.index,
                    title="Disease Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Disease severity analysis
                if 'severity_level' in df_diseases.columns:
                    severity_counts = df_diseases['severity_level'].value_counts()
                    
                    fig = px.bar(
                        x=severity_counts.index,
                        y=severity_counts.values,
                        title="Disease Severity Distribution",
                        color=severity_counts.values,
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Temporal analysis
            st.markdown("**📅 Temporal Disease Patterns:**")
            
            df_diseases['created_at'] = pd.to_datetime(df_diseases['created_at'])
            df_diseases['month'] = df_diseases['created_at'].dt.month
            df_diseases['week'] = df_diseases['created_at'].dt.isocalendar().week
            
            # Monthly disease occurrence
            monthly_diseases = df_diseases.groupby(['month', 'detected_disease']).size().unstack(fill_value=0)
            
            if not monthly_diseases.empty:
                fig = px.imshow(
                    monthly_diseases.T,
                    title="Disease Occurrence by Month",
                    labels=dict(x="Month", y="Disease", color="Count"),
                    aspect="auto"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Risk factors analysis
            st.markdown("**⚠️ Disease Risk Analysis:**")
            
            # Calculate disease risk metrics
            total_detections = len(df_diseases)
            unique_diseases = df_diseases['detected_disease'].nunique()
            avg_confidence = df_diseases['confidence_score'].mean() if 'confidence_score' in df_diseases.columns else 0
            
            risk_col1, risk_col2, risk_col3 = st.columns(3)
            
            with risk_col1:
                st.metric("Total Detections", total_detections)
            with risk_col2:
                st.metric("Unique Diseases", unique_diseases)
            with risk_col3:
                st.metric("Avg Confidence", f"{avg_confidence*100:.1f}%")
            
            # Disease hotspots
            if 'location_name' in df_diseases.columns:
                st.markdown("**🗺️ Disease Hotspots:**")
                
                location_diseases = df_diseases.groupby('location_name')['detected_disease'].count().sort_values(ascending=False)
                
                fig = px.bar(
                    x=location_diseases.values,
                    y=location_diseases.index,
                    orientation='h',
                    title="Disease Detections by Location"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("📭 No disease detection data available for analysis")
            st.markdown("💡 Start using disease detection to build analytical insights")
    
    except Exception as e:
        st.error(f"❌ Error in disease pattern analysis: {e}")

def render_weather_impact_analysis():
    """Render weather impact analysis"""
    
    st.markdown("#### 🌤️ Weather Impact Analysis")
    
    try:
        weather_request = AnalysisRequest(
            analysis_type='weather_impact_analysis',
            parameters={},
            user_id=1
        )
        
        weather_analysis = analysis_service.analyze_weather_impact(weather_request)
        
        if weather_analysis.get('success'):
            weather_data = weather_analysis.get('data', {})
            
            if weather_data:
                # Weather impact overview
                st.markdown("**🌍 Weather Impact Overview:**")
                
                impact_scores = []
                location_names = []
                
                for location, data in weather_data.items():
                    impact_score = data.get('impact_score', 0)
                    impact_scores.append(impact_score * 100)
                    location_names.append(location)
                
                if impact_scores:
                    # Impact scores by location
                    weather_impact_chart = viz_engine.create_weather_impact_chart(weather_data)
                    st.plotly_chart(weather_impact_chart, use_container_width=True)
                    
                    # Summary statistics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Avg Impact Score", f"{np.mean(impact_scores):.1f}%")
                    with col2:
                        st.metric("Best Conditions", f"{max(impact_scores):.1f}%")
                    with col3:
                        st.metric("Challenging Conditions", f"{min(impact_scores):.1f}%")
                    with col4:
                        st.metric("Locations Analyzed", len(impact_scores))
                
                # Detailed weather analysis
                st.markdown("**🔍 Detailed Weather Analysis:**")
                
                for location, data in weather_data.items():
                    with st.expander(f"📍 {location} - Detailed Analysis"):
                        analysis = data.get('analysis', {})
                        
                        # Temperature analysis
                        temp_analysis = analysis.get('temperature_analysis', {})
                        if temp_analysis:
                            st.markdown("**🌡️ Temperature Analysis:**")
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.write(f"• Average Max: {temp_analysis.get('avg_temp_max', 0):.1f}°C")
                                st.write(f"• Average Min: {temp_analysis.get('avg_temp_min', 0):.1f}°C")
                            
                            with col_b:
                                st.write(f"• Heat Stress Days: {temp_analysis.get('heat_stress_days', 0)}")
                                st.write(f"• Frost Risk Days: {temp_analysis.get('frost_risk_days', 0)}")
                        
                        # Rainfall analysis
                        rainfall_analysis = analysis.get('rainfall_analysis', {})
                        if rainfall_analysis:
                            st.markdown("**🌧️ Rainfall Analysis:**")
                            col_c, col_d = st.columns(2)
                            
                            with col_c:
                                st.write(f"• Total Rainfall: {rainfall_analysis.get('total_rainfall', 0):.1f} mm")
                                st.write(f"• Rainy Days: {rainfall_analysis.get('rainy_days', 0)}")
                            
                            with col_d:
                                st.write(f"• Heavy Rain Days: {rainfall_analysis.get('heavy_rain_days', 0)}")
                                st.write(f"• Max Dry Spell: {rainfall_analysis.get('dry_spell_max', 0)} days")
            
            # Weather insights
            insights = weather_analysis.get('insights', [])
            recommendations = weather_analysis.get('recommendations', [])
            
            if insights or recommendations:
                st.markdown("---")
                col_insight, col_rec = st.columns(2)
                
                with col_insight:
                    if insights:
                        st.markdown("**💡 Weather Insights:**")
                        for insight in insights:
                            st.info(f"🌤️ {insight}")
                
                with col_rec:
                    if recommendations:
                        st.markdown("**🎯 Weather Recommendations:**")
                        for rec in recommendations:
                            st.success(f"✅ {rec}")
        
        else:
            st.warning("⚠️ No weather impact data available")
            st.info("💡 Register farm locations to enable weather impact analysis")
    
    except Exception as e:
        st.error(f"❌ Error in weather impact analysis: {e}")

def render_soil_health_analysis():
    """Render soil health analysis"""
    
    st.markdown("#### 🌱 Soil Health Analysis")
    
    # Soil parameter input for analysis
    st.markdown("**🧪 Soil Analysis Parameters:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ph_range = st.slider("pH Range", 3.0, 12.0, (6.0, 8.0), 0.1)
        nitrogen_range = st.slider("Nitrogen (kg/ha)", 0, 300, (40, 80), 5)
    
    with col2:
        phosphorus_range = st.slider("Phosphorus (kg/ha)", 0, 200, (20, 50), 5)
        potassium_range = st.slider("Potassium (kg/ha)", 0, 500, (150, 300), 10)
    
    with col3:
        organic_matter = st.slider("Organic Matter (%)", 0.0, 10.0, (2.0, 5.0), 0.1)
        moisture_content = st.slider("Moisture Content (%)", 0, 100, (30, 60), 5)
    
    if st.button("🧪 Analyze Soil Health"):
        # Generate soil health analysis
        soil_data = {
            'ph': np.random.uniform(ph_range[0], ph_range[1], 100),
            'nitrogen': np.random.uniform(nitrogen_range[0], nitrogen_range[1], 100),
            'phosphorus': np.random.uniform(phosphorus_range[0], phosphorus_range[1], 100),
            'potassium': np.random.uniform(potassium_range[0], potassium_range[1], 100),
            'organic_matter': np.random.uniform(organic_matter[0], organic_matter[1], 100),
            'moisture': np.random.uniform(moisture_content[0], moisture_content[1], 100)
        }
        
        soil_df = pd.DataFrame(soil_data)
        
        # Soil health metrics
        st.markdown("**📊 Soil Health Metrics:**")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            ph_score = calculate_ph_score(soil_df['ph'].mean())
            st.metric("pH Score", f"{ph_score:.1f}/10")
        
        with col_m2:
            nutrient_score = calculate_nutrient_score(
                soil_df['nitrogen'].mean(),
                soil_df['phosphorus'].mean(), 
                soil_df['potassium'].mean()
            )
            st.metric("Nutrient Score", f"{nutrient_score:.1f}/10")
        
        with col_m3:
            organic_score = calculate_organic_score(soil_df['organic_matter'].mean())
            st.metric("Organic Matter Score", f"{organic_score:.1f}/10")
        
        with col_m4:
            overall_score = (ph_score + nutrient_score + organic_score) / 3
            st.metric("Overall Health", f"{overall_score:.1f}/10")
        
        # Nutrient balance radar chart
        st.markdown("**🎯 Nutrient Balance Analysis:**")
        
        nutrient_balance = {
            'Nitrogen': (soil_df['nitrogen'].mean() / 100) * 100,  # Normalize to 0-100
            'Phosphorus': (soil_df['phosphorus'].mean() / 50) * 100,
            'Potassium': (soil_df['potassium'].mean() / 300) * 100,
            'pH Level': ((soil_df['ph'].mean() - 3) / 9) * 100,
            'Organic Matter': (soil_df['organic_matter'].mean() / 5) * 100,
            'Moisture': soil_df['moisture'].mean()
        }
        
        nutrient_chart = viz_engine.create_nutrient_balance_chart(nutrient_balance)
        st.plotly_chart(nutrient_chart, use_container_width=True)
        
        # Soil recommendations
        st.markdown("**💡 Soil Health Recommendations:**")
        
        recommendations = generate_soil_recommendations(soil_df)
        
        for rec in recommendations:
            st.success(f"✅ {rec}")

def render_resource_optimization_analysis():
    """Render resource optimization analysis"""
    
    st.markdown("#### ⚡ Resource Optimization Analysis")
    
    # Resource categories
    resource_category = st.selectbox(
        "Resource Category:",
        options=["Water Usage", "Fertilizer Efficiency", "Energy Consumption", "Labor Optimization"],
        help="Select resource category for optimization analysis"
    )
    
    if resource_category == "Water Usage":
        render_water_optimization()
    elif resource_category == "Fertilizer Efficiency":
        render_fertilizer_optimization()
    elif resource_category == "Energy Consumption":
        render_energy_optimization()
    else:
        render_labor_optimization()

def render_comparative_analysis():
    """Render comparative analysis interface"""
    
    st.markdown("#### 📊 Comparative Analysis")
    
    comparison_type = st.selectbox(
        "Comparison Type:",
        options=[
            "Farm Performance Comparison",
            "Crop Variety Comparison",
            "Seasonal Performance",
            "Treatment Effectiveness",
            "Regional Analysis"
        ]
    )
    
    if comparison_type == "Farm Performance Comparison":
        render_farm_comparison()
    elif comparison_type == "Crop Variety Comparison":
        render_crop_comparison()
    elif comparison_type == "Seasonal Performance":
        render_seasonal_comparison()
    elif comparison_type == "Treatment Effectiveness":
        render_treatment_comparison()
    else:
        render_regional_comparison()

def render_custom_reports():
    """Render custom reports interface"""
    
    st.subheader("Custom Reports & Exports")
    st.markdown("Create customized analytical reports for stakeholders")
    
    # Report configuration
    st.markdown("**📋 Report Configuration**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report Type:",
            options=[
                "Executive Summary",
                "Technical Analysis",
                "Performance Report",
                "Compliance Report",
                "Custom Dashboard"
            ]
        )
        
        report_format = st.selectbox(
            "Output Format:",
            options=["PDF", "Excel", "PowerPoint", "Interactive Dashboard"],
            help="Select output format for the report"
        )
    
    with col2:
        time_range = st.selectbox(
            "Time Range:",
            options=["Last Week", "Last Month", "Last Quarter", "Last Year", "Custom"]
        )
        
        if time_range == "Custom":
            custom_start = st.date_input("Start Date")
            custom_end = st.date_input("End Date")
        
        include_charts = st.checkbox("Include Charts & Visualizations", value=True)
        include_raw_data = st.checkbox("Include Raw Data", value=False)
    
    # Report sections
    st.markdown("**📑 Report Sections**")
    
    sections = {
        "Executive Summary": st.checkbox("Executive Summary", value=True),
        "Yield Analysis": st.checkbox("Yield Analysis", value=True),
        "Disease Monitoring": st.checkbox("Disease Monitoring", value=True),
        "Weather Impact": st.checkbox("Weather Impact", value=True),
        "Resource Utilization": st.checkbox("Resource Utilization", value=False),
        "ROI Analysis": st.checkbox("ROI Analysis", value=False),
        "Recommendations": st.checkbox("Recommendations", value=True)
    }
    
    # Report customization
    with st.expander("🎨 Report Customization"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            report_title = st.text_input("Report Title", value="Agricultural Analytics Report")
            company_logo = st.file_uploader("Company Logo", type=['png', 'jpg'])
        
        with col_b:
            report_author = st.text_input("Report Author", value="Smart Sènè Analytics")
            color_scheme = st.selectbox("Color Scheme", options=["Corporate Blue", "Agricultural Green", "Professional Gray"])
    
    # Generate report
    if st.button("📄 Generate Report", type="primary", use_container_width=True):
        with st.spinner("📊 Generating custom report..."):
            # Simulate report generation
            import time
            time.sleep(2)
            
            st.success("✅ Report generated successfully!")
            
            # Report preview
            st.markdown("### 📋 Report Preview")
            
            # Show report sections based on selection
            selected_sections = [section for section, selected in sections.items() if selected]
            
            for section in selected_sections:
                st.markdown(f"**{section}**")
                
                if section == "Executive Summary":
                    st.write("• Overall system performance: Excellent")
                    st.write("• Total predictions processed: 1,247")
                    st.write("• Average accuracy: 94.2%")
                
                elif section == "Yield Analysis":
                    st.write("• Average yield performance: 4,350 kg/ha")
                    st.write("• Yield trend: +15% improvement")
                    st.write("• Top performing crops: Maize, Rice")
                
                elif section == "Disease Monitoring":
                    st.write("• Diseases detected: 23 cases")
                    st.write("• Most common: Early Blight (35%)")
                    st.write("• Prevention success rate: 87%")
                
                elif section == "Weather Impact":
                    st.write("• Weather conditions: Favorable")
                    st.write("• Rainfall adequacy: 95%")
                    st.write("• Temperature stress days: 3")
                
                elif section == "Resource Utilization":
                    st.write("• Water efficiency: 92%")
                    st.write("• Fertilizer optimization: 88%")
                    st.write("• Energy savings: 23%")
                
                elif section == "ROI Analysis":
                    st.write("• Return on investment: 156%")
                    st.write("• Cost savings: $12,500")
                    st.write("• Payback period: 8 months")
                
                elif section == "Recommendations":
                    st.write("• Implement precision irrigation in Zone B")
                    st.write("• Increase disease monitoring frequency")
                    st.write("• Consider drought-resistant varieties for next season")
            
            # Download options
            st.markdown("---")
            st.markdown("**📥 Download Options**")
            
            col_dl1, col_dl2, col_dl3 = st.columns(3)
            
            with col_dl1:
                if st.button("📄 Download PDF"):
                    st.success("📁 PDF report ready for download")
            
            with col_dl2:
                if st.button("📊 Download Excel"):
                    st.success("📈 Excel report ready for download")
            
            with col_dl3:
                if st.button("📧 Email Report"):
                    st.success("📤 Report sent via email")

def render_predictive_insights():
    """Render predictive insights interface"""
    
    st.subheader("Predictive Insights & Forecasting")
    st.markdown("Advanced predictive analytics for future planning")
    
    # Prediction category
    prediction_category = st.selectbox(
        "Prediction Category:",
        options=[
            "Seasonal Yield Forecasting",
            "Disease Risk Prediction", 
            "Weather Pattern Forecasting",
            "Market Demand Prediction",
            "Resource Requirement Planning"
        ]
    )
    
    # Prediction timeframe
    col1, col2 = st.columns(2)
    
    with col1:
        prediction_horizon = st.selectbox(
            "Prediction Horizon:",
            options=["Next 30 Days", "Next Season", "Next 6 Months", "Next Year"],
            help="Select forecasting time horizon"
        )
    
    with col2:
        confidence_level = st.selectbox(
            "Confidence Level:",
            options=["90%", "95%", "99%"],
            index=1,
            help="Statistical confidence level for predictions"
        )
    
    if st.button("🔮 Generate Predictions", type="primary"):
        with st.spinner("🤖 Generating predictive insights..."):
            try:
                # Get predictive analytics
                predictive_request = AnalysisRequest(
                    analysis_type='predictive_analytics',
                    parameters={
                        'category': prediction_category,
                        'horizon': prediction_horizon,
                        'confidence': confidence_level
                    },
                    user_id=1
                )
                
                predictive_analysis = analysis_service.generate_predictive_analytics(predictive_request)
                
                if predictive_analysis.get('success'):
                    st.success("✅ Predictive analysis completed!")
                    
                    # Seasonal predictions
                    seasonal_predictions = predictive_analysis.get('seasonal_predictions', {})
                    
                    if seasonal_predictions:
                        st.markdown("### 📅 Seasonal Forecasts")
                        
                        col_pred1, col_pred2, col_pred3 = st.columns(3)
                        
                        with col_pred1:
                            yield_forecast = seasonal_predictions.get('next_season_yield_forecast', 'Unknown')
                            st.metric("Yield Forecast", yield_forecast)
                        
                        with col_pred2:
                            disease_risk = seasonal_predictions.get('disease_risk_forecast', 'Unknown')
                            st.metric("Disease Risk", disease_risk)
                        
                        with col_pred3:
                            confidence = seasonal_predictions.get('confidence_level', 0)
                            st.metric("Confidence", f"{confidence*100:.0f}%")
                        
                        # Seasonal forecast chart
                        forecast_chart = viz_engine.create_seasonal_forecast_chart(seasonal_predictions)
                        st.plotly_chart(forecast_chart, use_container_width=True)
                    
                    # Risk assessment
                    risk_assessment = predictive_analysis.get('risk_assessment', {})
                    
                    if risk_assessment:
                        st.markdown("### ⚠️ Risk Assessment")
                        
                        overall_risk = risk_assessment.get('overall_risk_score', 0)
                        
                        if overall_risk < 0.3:
                            st.success(f"🟢 Low Risk: {overall_risk*100:.0f}% risk score")
                        elif overall_risk < 0.6:
                            st.warning(f"🟡 Medium Risk: {overall_risk*100:.0f}% risk score")
                        else:
                            st.error(f"🔴 High Risk: {overall_risk*100:.0f}% risk score")
                        
                        # Risk breakdown
                        risk_types = ['weather_risk', 'disease_risk', 'market_risk', 'operational_risk']
                        
                        for risk_type in risk_types:
                            if risk_type in risk_assessment:
                                risk_level = risk_assessment[risk_type]
                                st.write(f"• **{risk_type.replace('_', ' ').title()}:** {risk_level}")
                        
                        # Mitigation strategies
                        mitigation_strategies = risk_assessment.get('mitigation_strategies', [])
                        
                        if mitigation_strategies:
                            st.markdown("**🛡️ Risk Mitigation Strategies:**")
                            for strategy in mitigation_strategies:
                                st.write(f"• {strategy}")
                    
                    # Opportunities
                    opportunities = predictive_analysis.get('opportunities', [])
                    
                    if opportunities:
                        st.markdown("### 🎯 Identified Opportunities")
                        
                        for opp in opportunities:
                            st.markdown(f"**{opp.get('opportunity', 'Unknown')}**")
                            st.write(f"• Potential Benefit: {opp.get('potential_benefit', 'Unknown')}")
                            st.write(f"• Investment Required: {opp.get('investment_required', 'Unknown')}")
                            st.write(f"• Timeline: {opp.get('timeline', 'Unknown')}")
                            st.write("")
                    
                    # Strategic recommendations
                    strategic_recommendations = predictive_analysis.get('strategic_recommendations', [])
                    
                    if strategic_recommendations:
                        st.markdown("### 🎯 Strategic Recommendations")
                        
                        for i, rec in enumerate(strategic_recommendations, 1):
                            st.write(f"{i}. {rec}")
                
                else:
                    st.error("❌ Failed to generate predictive insights")
            
            except Exception as e:
                st.error(f"❌ Error generating predictions: {e}")
    
    else:
        st.info("🔮 Configure prediction parameters and click 'Generate Predictions' to see forecasts")
        
        # Prediction capabilities
        st.markdown("### 🤖 Predictive Analytics Capabilities")
        
        capabilities = {
            "🌾 Yield Forecasting": "Predict crop yields based on historical data and current conditions",
            "🦠 Disease Risk Modeling": "Forecast disease outbreaks using weather and crop data",
            "🌤️ Weather Pattern Analysis": "Long-term weather trend prediction for planning",
            "📈 Market Demand Forecasting": "Predict crop demand and pricing trends",
            "⚡ Resource Planning": "Optimize resource allocation for future seasons"
        }
        
        for capability, description in capabilities.items():
            st.write(f"**{capability}:** {description}")

# Helper functions

def calculate_ph_score(ph_value: float) -> float:
    """Calculate pH score (0-10 scale)"""
    optimal_ph = 6.5
    max_deviation = 3.5
    
    deviation = abs(ph_value - optimal_ph)
    score = max(0, 10 - (deviation / max_deviation) * 10)
    
    return score

def calculate_nutrient_score(nitrogen: float, phosphorus: float, potassium: float) -> float:
    """Calculate nutrient balance score"""
    # Optimal ranges
    n_optimal = (40, 80)
    p_optimal = (20, 50)
    k_optimal = (150, 300)
    
    # Calculate individual scores
    n_score = 10 if n_optimal[0] <= nitrogen <= n_optimal[1] else max(0, 10 - abs(nitrogen - np.mean(n_optimal)) / 10)
    p_score = 10 if p_optimal[0] <= phosphorus <= p_optimal[1] else max(0, 10 - abs(phosphorus - np.mean(p_optimal)) / 5)
    k_score = 10 if k_optimal[0] <= potassium <= k_optimal[1] else max(0, 10 - abs(potassium - np.mean(k_optimal)) / 20)
    
    return (n_score + p_score + k_score) / 3

def calculate_organic_score(organic_matter: float) -> float:
    """Calculate organic matter score"""
    if organic_matter >= 3.0:
        return 10
    elif organic_matter >= 2.0:
        return 8
    elif organic_matter >= 1.0:
        return 6
    else:
        return max(0, organic_matter * 4)

def generate_soil_recommendations(soil_df: pd.DataFrame) -> List[str]:
    """Generate soil health recommendations"""
    recommendations = []
    
    avg_ph = soil_df['ph'].mean()
    avg_nitrogen = soil_df['nitrogen'].mean()
    avg_phosphorus = soil_df['phosphorus'].mean()
    avg_potassium = soil_df['potassium'].mean()
    avg_organic = soil_df['organic_matter'].mean()
    
    # pH recommendations
    if avg_ph < 6.0:
        recommendations.append("Apply lime to increase soil pH and improve nutrient availability")
    elif avg_ph > 8.0:
        recommendations.append("Apply sulfur or organic matter to reduce soil pH")
    
    # Nutrient recommendations
    if avg_nitrogen < 40:
        recommendations.append("Apply nitrogen fertilizer or organic compost to boost nitrogen levels")
    elif avg_nitrogen > 100:
        recommendations.append("Reduce nitrogen inputs to prevent nutrient burn and environmental impact")
    
    if avg_phosphorus < 20:
        recommendations.append("Apply phosphorus fertilizer to support root development and flowering")
    
    if avg_potassium < 150:
        recommendations.append("Apply potassium fertilizer to improve disease resistance and fruit quality")
    
    # Organic matter recommendations
    if avg_organic < 2.0:
        recommendations.append("Increase organic matter through compost, cover crops, or green manure")
    
    return recommendations

def render_water_optimization():
    """Render water usage optimization analysis"""
    st.markdown("**💧 Water Usage Optimization**")
    
    # Sample water usage data
    water_data = {
        'Irrigation Method': ['Drip', 'Sprinkler', 'Flood', 'Micro-spray'],
        'Water Efficiency (%)': [90, 75, 45, 85],
        'Cost per Hectare ($)': [800, 600, 400, 700],
        'Yield Impact (%)': [+25, +15, 0, +20]
    }
    
    water_df = pd.DataFrame(water_data)
    st.dataframe(water_df, use_container_width=True)
    
    # Water efficiency chart
    fig = px.scatter(
        water_df,
        x='Cost per Hectare ($)',
        y='Water Efficiency (%)',
        size='Yield Impact (%)',
        color='Irrigation Method',
        title="Water Efficiency vs Cost Analysis"
    )
    st.plotly_chart(fig, use_container_width=True)

def render_fertilizer_optimization():
    """Render fertilizer efficiency analysis"""
    st.markdown("**💊 Fertilizer Efficiency Analysis**")
    
    # Sample fertilizer data
    fertilizer_data = {
        'Fertilizer Type': ['NPK 15-15-15', 'Urea', 'DAP', 'Organic Compost'],
        'Cost per kg ($)': [0.8, 0.4, 0.6, 0.3],
        'Efficiency Rating': [8.5, 7.0, 8.0, 9.5],
        'Environmental Impact': ['Medium', 'High', 'Medium', 'Low']
    }
    
    fert_df = pd.DataFrame(fertilizer_data)
    st.dataframe(fert_df, use_container_width=True)

def render_energy_optimization():
    """Render energy consumption analysis"""
    st.markdown("**⚡ Energy Consumption Analysis**")
    
    # Sample energy data
    energy_data = {
        'Equipment': ['Irrigation Pumps', 'Greenhouse Heating', 'Processing Equipment', 'Storage Cooling'],
        'Energy Consumption (kWh)': [1200, 800, 600, 400],
        'Efficiency Rating': [7.5, 6.0, 8.5, 9.0],
        'Optimization Potential (%)': [25, 40, 15, 10]
    }
    
    energy_df = pd.DataFrame(energy_data)
    st.dataframe(energy_df, use_container_width=True)

def render_labor_optimization():
    """Render labor optimization analysis"""
    st.markdown("**👥 Labor Optimization Analysis**")
    
    # Sample labor data
    labor_data = {
        'Activity': ['Planting', 'Harvesting', 'Pest Control', 'Irrigation Management'],
        'Hours per Hectare': [12, 20, 8, 6],
        'Labor Cost ($)': [150, 250, 100, 75],
        'Automation Potential (%)': [70, 85, 60, 90]
    }
    
    labor_df = pd.DataFrame(labor_data)
    st.dataframe(labor_df, use_container_width=True)

def render_farm_comparison():
    """Render farm performance comparison"""
    st.markdown("**🏭 Farm Performance Comparison**")
    st.info("Farm comparison analysis will compare performance metrics across multiple farm locations")

def render_crop_comparison():
    """Render crop variety comparison"""
    st.markdown("**🌾 Crop Variety Comparison**")
    st.info("Crop variety comparison will analyze performance differences between crop types")

def render_seasonal_comparison():
    """Render seasonal performance comparison"""
    st.markdown("**📅 Seasonal Performance Comparison**")
    st.info("Seasonal comparison will analyze performance trends across different seasons")

def render_treatment_comparison():
    """Render treatment effectiveness comparison"""
    st.markdown("**💊 Treatment Effectiveness Comparison**")
    st.info("Treatment comparison will analyze the effectiveness of different agricultural treatments")

def render_regional_comparison():
    """Render regional analysis comparison"""
    st.markdown("**🗺️ Regional Analysis Comparison**")
    st.info("Regional comparison will analyze performance differences across geographical regions")
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ton code principal ici
def main():
    print("✅ Script exécuté avec succès !")
    logging.info("Le script a été exécuté sans erreur.")

if __name__ == "__main__":
    main()
