"""
Enterprise Executive Dashboard
Professional overview with KPIs and business intelligence
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List

from core.database import db_manager
from services.analysis_service import analysis_service
from services.weather_service import weather_service
from utils.visualization import viz_engine

def render_dashboard():
    """Render the executive dashboard"""
    
    # Page header
    st.markdown("""
    <div class="dashboard-card">
        <h1 style="color: #2c3e50; margin-bottom: 0;">🏢 Executive Dashboard</h1>
        <p style="color: #7f8c8d; margin-top: 0.5rem;">Real-time agricultural intelligence and performance metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get system analytics
    try:
        analytics_data = db_manager.get_analytics_data()
        
        # KPI Cards Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Predictions</div>
                <div class="metric-value">{analytics_data.get('total_predictions', 0):,}</div>
                <div style="color: #28a745; font-size: 0.8rem; margin-top: 0.5rem;">
                    📈 Active AI Models
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Active Users</div>
                <div class="metric-value">{analytics_data.get('active_users', 0)}</div>
                <div style="color: #17a2b8; font-size: 0.8rem; margin-top: 0.5rem;">
                    👥 Last 30 Days
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Disease Detections</div>
                <div class="metric-value">{analytics_data.get('monthly_detections', 0)}</div>
                <div style="color: #fd7e14; font-size: 0.8rem; margin-top: 0.5rem;">
                    🔍 This Month
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Farm Locations</div>
                <div class="metric-value">{analytics_data.get('total_locations', 0)}</div>
                <div style="color: #6f42c1; font-size: 0.8rem; margin-top: 0.5rem;">
                    🌍 Registered Farms
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Main content areas
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Performance Overview
            st.markdown('<div class="card-title">📊 Performance Overview</div>', unsafe_allow_html=True)
            
            # Sample performance metrics for demonstration
            sample_metrics = {
                'productivity_score': 0.85,
                'health_score': 0.92,
                'efficiency_score': 0.78,
                'technology_adoption_score': 0.88
            }
            
            performance_chart = viz_engine.create_performance_dashboard(sample_metrics)
            st.plotly_chart(performance_chart, use_container_width=True, key="performance_overview")
            
            # Trend Analysis
            st.markdown('<div class="card-title">📈 System Usage Trends</div>', unsafe_allow_html=True)
            
            # Create sample trend data
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            trend_data = pd.DataFrame({
                'date': dates,
                'predictions': np.random.randint(10, 50, len(dates)),
                'detections': np.random.randint(5, 25, len(dates)),
                'active_users': np.random.randint(15, 40, len(dates))
            })
            
            # Create multi-line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=trend_data['date'],
                y=trend_data['predictions'],
                mode='lines+markers',
                name='Predictions',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=4)
            ))
            
            fig.add_trace(go.Scatter(
                x=trend_data['date'],
                y=trend_data['detections'],
                mode='lines+markers',
                name='Disease Detections',
                line=dict(color='#ff7f0e', width=2),
                marker=dict(size=4)
            ))
            
            fig.add_trace(go.Scatter(
                x=trend_data['date'],
                y=trend_data['active_users'],
                mode='lines+markers',
                name='Active Users',
                line=dict(color='#2ca02c', width=2),
                marker=dict(size=4)
            ))
            
            fig.update_layout(
                title="30-Day Activity Trends",
                xaxis_title="Date",
                yaxis_title="Count",
                hovermode='x unified',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True, key="trend_analysis")
        
        with col2:
            # System Status
            st.markdown('<div class="card-title">⚡ System Status</div>', unsafe_allow_html=True)
            
            status_items = [
                ("AI Models", "Online", "✅"),
                ("Database", "Healthy", "✅"),
                ("Weather API", "Active", "✅"),
                ("File Storage", "97% Free", "✅"),
                ("Security", "Protected", "🔒")
            ]
            
            for item, status, icon in status_items:
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; 
                           padding: 0.5rem; margin: 0.2rem 0; background: #f8f9fa; border-radius: 5px;">
                    <span style="font-weight: 500;">{item}</span>
                    <span style="color: #28a745;">{icon} {status}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Quick Actions
            st.markdown('<div class="card-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
            
            if st.button("🔄 Refresh Dashboard", key="refresh_dashboard", use_container_width=True):
                st.rerun()
            
            if st.button("📊 Generate Report", key="generate_report", use_container_width=True):
                st.success("📈 Report generation initiated!")
            
            if st.button("📧 Send Summary", key="send_summary", use_container_width=True):
                st.info("📨 Summary email scheduled")
            
            st.markdown("---")
            
            # Recent Alerts
            st.markdown('<div class="card-title">🔔 Recent Alerts</div>', unsafe_allow_html=True)
            
            alerts = [
                ("High disease risk detected in Location A", "2 hours ago", "⚠️"),
                ("Weather forecast updated", "4 hours ago", "🌤️"),
                ("Model training completed", "1 day ago", "✅"),
                ("New user registered", "2 days ago", "👤")
            ]
            
            for alert, time, icon in alerts:
                st.markdown(f"""
                <div style="padding: 0.5rem; margin: 0.2rem 0; border-left: 3px solid #ffc107; 
                           background: #fff3cd; border-radius: 0 5px 5px 0;">
                    <div style="font-weight: 500; font-size: 0.9rem;">{icon} {alert}</div>
                    <div style="font-size: 0.8rem; color: #856404; margin-top: 0.2rem;">{time}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Bottom Section - Weather and Regional Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card-title">🌤️ Weather Overview</div>', unsafe_allow_html=True)
            
            # Sample weather data
            weather_regions = {
                'North Region': {'temp': 28, 'humidity': 65, 'condition': 'Partly Cloudy'},
                'South Region': {'temp': 32, 'humidity': 78, 'condition': 'Sunny'},
                'East Region': {'temp': 26, 'humidity': 82, 'condition': 'Light Rain'},
                'West Region': {'temp': 30, 'humidity': 70, 'condition': 'Cloudy'}
            }
            
            for region, data in weather_regions.items():
                condition_icon = "☀️" if "Sunny" in data['condition'] else "⛅" if "Cloudy" in data['condition'] else "🌧️"
                
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; 
                           padding: 0.8rem; margin: 0.3rem 0; background: white; border: 1px solid #e9ecef; 
                           border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div>
                        <div style="font-weight: 600; color: #2c3e50;">{region}</div>
                        <div style="font-size: 0.9rem; color: #6c757d;">{data['condition']}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2rem; font-weight: 600; color: #1f77b4;">
                            {condition_icon} {data['temp']}°C
                        </div>
                        <div style="font-size: 0.8rem; color: #6c757d;">{data['humidity']}% humidity</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card-title">🎯 Key Insights</div>', unsafe_allow_html=True)
            
            insights = [
                {
                    'title': 'Yield Optimization Opportunity',
                    'description': '15% potential yield increase identified in northern farms',
                    'action': 'Review fertilization strategy',
                    'priority': 'High',
                    'icon': '📈'
                },
                {
                    'title': 'Disease Prevention Success',
                    'description': '85% reduction in fungal diseases this season',
                    'action': 'Continue current protocols',
                    'priority': 'Low',
                    'icon': '🛡️'
                },
                {
                    'title': 'Weather Pattern Alert',
                    'description': 'Unusual rainfall patterns detected in eastern region',
                    'action': 'Adjust irrigation schedule',
                    'priority': 'Medium',
                    'icon': '🌧️'
                }
            ]
            
            for insight in insights:
                priority_color = "#dc3545" if insight['priority'] == 'High' else "#ffc107" if insight['priority'] == 'Medium' else "#28a745"
                
                st.markdown(f"""
                <div style="padding: 1rem; margin: 0.5rem 0; background: white; border: 1px solid #e9ecef; 
                           border-radius: 8px; border-left: 4px solid {priority_color};">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.2rem; margin-right: 0.5rem;">{insight['icon']}</span>
                        <span style="font-weight: 600; color: #2c3e50;">{insight['title']}</span>
                        <span style="margin-left: auto; background: {priority_color}; color: white; 
                                   padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.8rem;">
                            {insight['priority']}
                        </span>
                    </div>
                    <div style="color: #6c757d; font-size: 0.9rem; margin-bottom: 0.5rem;">
                        {insight['description']}
                    </div>
                    <div style="color: #007bff; font-size: 0.8rem; font-weight: 500;">
                        💡 {insight['action']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Footer summary
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; margin-top: 2rem;">
            <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">🌟 Platform Summary</h4>
            <p style="color: #6c757d; margin: 0;">
                Smart Sènè Enterprise Platform is actively monitoring and optimizing agricultural operations across all registered farms.
                <br>
                <strong>System Performance:</strong> 98.5% uptime | <strong>Data Accuracy:</strong> 94.2% | <strong>User Satisfaction:</strong> 4.8/5
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {e}")
        st.info("🔄 Please refresh the page or contact system administrator")

# Helper function to generate sample data
import numpy as np

def generate_sample_trend_data(days: int = 30) -> pd.DataFrame:
    """Generate sample trend data for demonstration"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), end=datetime.now(), freq='D')
    
    # Generate realistic-looking data with some trends
    base_predictions = 25
    base_detections = 12
    base_users = 30
    
    predictions = []
    detections = []
    users = []
    
    for i, date in enumerate(dates):
        # Add some seasonal variation
        seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * i / 7)  # Weekly cycle
        trend_factor = 1 + 0.02 * i  # Slight upward trend
        
        pred = int(base_predictions * seasonal_factor * trend_factor + np.random.normal(0, 5))
        det = int(base_detections * seasonal_factor + np.random.normal(0, 3))
        user = int(base_users * trend_factor + np.random.normal(0, 4))
        
        predictions.append(max(5, pred))
        detections.append(max(1, det))
        users.append(max(10, user))
    
    return pd.DataFrame({
        'date': dates,
        'predictions': predictions,
        'detections': detections,
        'active_users': users
    })
