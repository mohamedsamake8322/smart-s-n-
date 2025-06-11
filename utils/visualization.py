"""
Enterprise Visualization Utilities
Professional charts and graphs for agricultural data
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

logger = logging.getLogger(__name__)

class VisualizationEngine:
    """Enterprise visualization engine with professional styling"""
    
    def __init__(self):
        # Professional color schemes
        self.color_schemes = {
            'primary': ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b'],
            'agricultural': ['#2e8b57', '#228b22', '#32cd32', '#9acd32', '#adff2f', '#7cfc00'],
            'enterprise': ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087', '#f95d6a'],
            'status': ['#28a745', '#ffc107', '#dc3545', '#17a2b8', '#6c757d'],
            'performance': ['#0d6efd', '#198754', '#ffc107', '#dc3545']
        }
        
        # Professional layout template
        self.layout_template = {
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'font': {'family': 'Arial, sans-serif', 'size': 12, 'color': '#2c3e50'},
            'title': {'font': {'size': 18, 'color': '#2c3e50'}, 'x': 0.5, 'xanchor': 'center'},
            'xaxis': {
                'showgrid': True,
                'gridcolor': '#e9ecef',
                'gridwidth': 1,
                'zeroline': False,
                'showline': True,
                'linecolor': '#dee2e6',
                'tickfont': {'size': 10}
            },
            'yaxis': {
                'showgrid': True,
                'gridcolor': '#e9ecef',
                'gridwidth': 1,
                'zeroline': False,
                'showline': True,
                'linecolor': '#dee2e6',
                'tickfont': {'size': 10}
            },
            'legend': {
                'orientation': 'h',
                'yanchor': 'bottom',
                'y': -0.2,
                'xanchor': 'center',
                'x': 0.5,
                'font': {'size': 10}
            },
            'margin': {'l': 60, 'r': 30, 't': 80, 'b': 80}
        }
    
    def create_yield_trend_chart(self, data: pd.DataFrame, 
                                title: str = "Yield Trends Over Time") -> go.Figure:
        """Create professional yield trend visualization"""
        try:
            fig = go.Figure()
            
            # Ensure we have the required columns
            if 'date' not in data.columns or 'yield' not in data.columns:
                # Create sample structure if missing
                if 'created_at' in data.columns:
                    data['date'] = pd.to_datetime(data['created_at']).dt.date
                if 'yield_value' in data.columns:
                    data['yield'] = data['yield_value']
            
            # Group by date for trend line
            if len(data) > 0:
                daily_avg = data.groupby('date')['yield'].mean().reset_index()
                
                # Main trend line
                fig.add_trace(go.Scatter(
                    x=daily_avg['date'],
                    y=daily_avg['yield'],
                    mode='lines+markers',
                    name='Average Yield',
                    line=dict(color=self.color_schemes['primary'][0], width=3),
                    marker=dict(size=8, symbol='circle'),
                    hovertemplate='<b>Date:</b> %{x}<br><b>Yield:</b> %{y:.1f} kg/ha<extra></extra>'
                ))
                
                # Add trend line
                if len(daily_avg) > 1:
                    z = np.polyfit(range(len(daily_avg)), daily_avg['yield'], 1)
                    trend_line = np.poly1d(z)(range(len(daily_avg)))
                    
                    fig.add_trace(go.Scatter(
                        x=daily_avg['date'],
                        y=trend_line,
                        mode='lines',
                        name='Trend',
                        line=dict(color=self.color_schemes['enterprise'][3], width=2, dash='dash'),
                        hovertemplate='<b>Trend:</b> %{y:.1f} kg/ha<extra></extra>'
                    ))
                
                # Add confidence band if we have enough data
                if len(daily_avg) > 5:
                    std_dev = data.groupby('date')['yield'].std().fillna(0)
                    upper_bound = daily_avg['yield'] + std_dev
                    lower_bound = daily_avg['yield'] - std_dev
                    
                    fig.add_trace(go.Scatter(
                        x=daily_avg['date'].tolist() + daily_avg['date'].tolist()[::-1],
                        y=upper_bound.tolist() + lower_bound.tolist()[::-1],
                        fill='toself',
                        fillcolor='rgba(31, 119, 180, 0.2)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='Confidence Band',
                        showlegend=False,
                        hoverinfo='skip'
                    ))
            
            # Apply professional styling
            fig.update_layout(
                title=title,
                xaxis_title="Date",
                yaxis_title="Yield (kg/ha)",
                **self.layout_template
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating yield trend chart: {e}")
            return self._create_error_chart("Error creating yield trend chart")
    
    def create_performance_dashboard(self, metrics: Dict[str, float]) -> go.Figure:
        """Create executive performance dashboard"""
        try:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Productivity Score', 'Health Score', 'Efficiency Score', 'Technology Score'],
                specs=[[{"type": "indicator"}, {"type": "indicator"}],
                      [{"type": "indicator"}, {"type": "indicator"}]]
            )
            
            # Performance metrics with thresholds
            performance_configs = [
                ('productivity_score', 'Productivity', 1, 1),
                ('health_score', 'Health', 1, 2),
                ('efficiency_score', 'Efficiency', 2, 1),
                ('technology_adoption_score', 'Technology', 2, 2)
            ]
            
            for metric_key, title, row, col in performance_configs:
                value = metrics.get(metric_key, 0) * 100  # Convert to percentage
                
                # Determine color based on performance
                if value >= 80:
                    color = self.color_schemes['status'][0]  # Green
                elif value >= 60:
                    color = self.color_schemes['status'][1]  # Yellow
                else:
                    color = self.color_schemes['status'][2]  # Red
                
                fig.add_trace(go.Indicator(
                    mode="gauge+number+delta",
                    value=value,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': title, 'font': {'size': 16}},
                    delta={'reference': 75, 'increasing': {'color': "green"}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': color},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 50], 'color': '#ffebee'},
                            {'range': [50, 75], 'color': '#fff3e0'},
                            {'range': [75, 100], 'color': '#e8f5e8'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ), row=row, col=col)
            
            fig.update_layout(
                title="Farm Performance Dashboard",
                height=600,
                **self.layout_template
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating performance dashboard: {e}")
            return self._create_error_chart("Error creating performance dashboard")
    
    def create_disease_distribution_chart(self, disease_data: List[Dict]) -> go.Figure:
        """Create disease distribution visualization"""
        try:
            if not disease_data:
                return self._create_empty_chart("No disease data available")
            
            # Process disease data
            df = pd.DataFrame(disease_data)
            disease_counts = df['detected_disease'].value_counts()
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=disease_counts.index,
                values=disease_counts.values,
                hole=0.4,
                marker=dict(
                    colors=self.color_schemes['agricultural'],
                    line=dict(color='#FFFFFF', width=2)
                ),
                textinfo='label+percent',
                textposition='outside',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            # Add center text
            fig.add_annotation(
                text=f"Total<br>{disease_counts.sum()}",
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False
            )
            
            fig.update_layout(
                title="Disease Distribution Analysis",
                **self.layout_template
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating disease distribution chart: {e}")
            return self._create_error_chart("Error creating disease distribution chart")
    
    def create_weather_impact_chart(self, weather_data: Dict[str, Any]) -> go.Figure:
        """Create weather impact visualization"""
        try:
            if not weather_data:
                return self._create_empty_chart("No weather data available")
            
            # Extract locations and impact scores
            locations = list(weather_data.keys())
            impact_scores = [data.get('impact_score', 0) * 100 for data in weather_data.values()]
            
            # Color mapping based on impact score
            colors = []
            for score in impact_scores:
                if score >= 70:
                    colors.append(self.color_schemes['status'][0])  # Green
                elif score >= 50:
                    colors.append(self.color_schemes['status'][1])  # Yellow
                else:
                    colors.append(self.color_schemes['status'][2])  # Red
            
            fig = go.Figure(data=[go.Bar(
                x=locations,
                y=impact_scores,
                marker=dict(color=colors, line=dict(color='white', width=1)),
                text=[f"{score:.1f}%" for score in impact_scores],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Impact Score: %{y:.1f}%<extra></extra>'
            )])
            
            # Add reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="green", 
                         annotation_text="Good Conditions")
            fig.add_hline(y=50, line_dash="dash", line_color="orange", 
                         annotation_text="Moderate Conditions")
            
            fig.update_layout(
                title="Weather Impact Assessment by Location",
                xaxis_title="Farm Locations",
                yaxis_title="Weather Impact Score (%)",
                yaxis=dict(range=[0, 100]),
                **self.layout_template
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating weather impact chart: {e}")
            return self._create_error_chart("Error creating weather impact chart")
    
    def create_roi_comparison_chart(self, roi_data: Dict[str, Dict]) -> go.Figure:
        """Create ROI comparison visualization"""
        try:
            if not roi_data:
                return self._create_empty_chart("No ROI data available")
            
            # Extract data for comparison
            categories = []
            roi_values = []
            payback_periods = []
            
            for category, data in roi_data.items():
                categories.append(category.replace('_', ' ').title())
                roi_values.append(data.get('roi_percentage', 0))
                payback_periods.append(data.get('payback_period_months', 0))
            
            # Create dual axis chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # ROI bars
            fig.add_trace(go.Bar(
                x=categories,
                y=roi_values,
                name='ROI %',
                marker=dict(color=self.color_schemes['performance'][0]),
                yaxis='y',
                hovertemplate='<b>%{x}</b><br>ROI: %{y}%<extra></extra>'
            ), secondary_y=False)
            
            # Payback period line
            fig.add_trace(go.Scatter(
                x=categories,
                y=payback_periods,
                mode='lines+markers',
                name='Payback Period (months)',
                line=dict(color=self.color_schemes['performance'][2], width=3),
                marker=dict(size=10),
                yaxis='y2',
                hovertemplate='<b>%{x}</b><br>Payback: %{y} months<extra></extra>'
            ), secondary_y=True)
            
            # Update axes titles
            fig.update_xaxes(title_text="Investment Category")
            fig.update_yaxes(title_text="ROI Percentage (%)", secondary_y=False)
            fig.update_yaxes(title_text="Payback Period (Months)", secondary_y=True)
            
            fig.update_layout(
                title="Investment ROI Comparison",
                **self.layout_template
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating ROI comparison chart: {e}")
            return self._create_error_chart("Error creating ROI comparison chart")
    
    def create_seasonal_forecast_chart(self, forecast_data: Dict[str, Any]) -> go.Figure:
        """Create seasonal forecast visualization"""
        try:
            # Generate sample forecast data if none provided
            if not forecast_data:
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                yield_forecast = [3200, 3400, 4100, 4500, 4800, 4600,
                                4400, 4200, 3900, 3600, 3300, 3100]
                confidence_upper = [y * 1.15 for y in yield_forecast]
                confidence_lower = [y * 0.85 for y in yield_forecast]
            else:
                months = forecast_data.get('months', [])
                yield_forecast = forecast_data.get('yield_forecast', [])
                confidence_upper = forecast_data.get('confidence_upper', [])
                confidence_lower = forecast_data.get('confidence_lower', [])
            
            fig = go.Figure()
            
            # Confidence band
            if confidence_upper and confidence_lower:
                fig.add_trace(go.Scatter(
                    x=months + months[::-1],
                    y=confidence_upper + confidence_lower[::-1],
                    fill='toself',
                    fillcolor='rgba(31, 119, 180, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='Confidence Range',
                    showlegend=True,
                    hoverinfo='skip'
                ))
            
            # Main forecast line
            fig.add_trace(go.Scatter(
                x=months,
                y=yield_forecast,
                mode='lines+markers',
                name='Yield Forecast',
                line=dict(color=self.color_schemes['primary'][0], width=3),
                marker=dict(size=10, symbol='diamond'),
                hovertemplate='<b>%{x}</b><br>Forecast: %{y:.0f} kg/ha<extra></extra>'
            ))
            
            fig.update_layout(
                title="Seasonal Yield Forecast",
                xaxis_title="Month",
                yaxis_title="Predicted Yield (kg/ha)",
                **self.layout_template
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating seasonal forecast chart: {e}")
            return self._create_error_chart("Error creating seasonal forecast chart")
    
    def create_nutrient_balance_chart(self, nutrient_data: Dict[str, float]) -> go.Figure:
        """Create nutrient balance radar chart"""
        try:
            # Default nutrients if none provided
            if not nutrient_data:
                nutrient_data = {
                    'Nitrogen': 75,
                    'Phosphorus': 60,
                    'Potassium': 85,
                    'Calcium': 70,
                    'Magnesium': 55,
                    'Sulfur': 65
                }
            
            nutrients = list(nutrient_data.keys())
            values = list(nutrient_data.values())
            
            fig = go.Figure()
            
            # Add radar chart
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=nutrients,
                fill='toself',
                fillcolor='rgba(46, 139, 87, 0.3)',
                line=dict(color=self.color_schemes['agricultural'][0], width=2),
                name='Current Levels',
                hovertemplate='<b>%{theta}</b><br>Level: %{r}%<extra></extra>'
            ))
            
            # Add optimal range
            optimal_values = [80] * len(nutrients)  # Assuming 80% is optimal
            fig.add_trace(go.Scatterpolar(
                r=optimal_values,
                theta=nutrients,
                mode='lines',
                line=dict(color='red', width=2, dash='dash'),
                name='Optimal Level',
                hovertemplate='<b>%{theta}</b><br>Optimal: %{r}%<extra></extra>'
            ))
            
            fig.update_layout(
                title="Soil Nutrient Balance Analysis",
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        ticksuffix='%'
                    )
                ),
                **self.layout_template
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating nutrient balance chart: {e}")
            return self._create_error_chart("Error creating nutrient balance chart")
    
    def create_cost_benefit_analysis(self, cost_data: Dict[str, Dict]) -> go.Figure:
        """Create cost-benefit analysis waterfall chart"""
        try:
            if not cost_data:
                return self._create_empty_chart("No cost-benefit data available")
            
            # Extract data for waterfall chart
            categories = ['Initial Investment']
            values = [-5000]  # Initial cost
            colors = ['red']
            
            for category, data in cost_data.items():
                benefit = data.get('revenue_increase', 0)
                categories.append(category.replace('_', ' ').title())
                values.append(benefit)
                colors.append('green')
            
            # Add total
            categories.append('Net Benefit')
            values.append(sum(values[1:]) + values[0])  # Net calculation
            colors.append('blue' if values[-1] > 0 else 'red')
            
            fig = go.Figure(go.Waterfall(
                name="Cost-Benefit Analysis",
                orientation="v",
                measure=["absolute"] + ["relative"] * (len(categories) - 2) + ["total"],
                x=categories,
                textposition="outside",
                text=[f"${val:,.0f}" for val in values],
                y=values,
                connector={"line": {"color": "rgb(63, 63, 63)"}},
                increasing={"marker": {"color": self.color_schemes['status'][0]}},
                decreasing={"marker": {"color": self.color_schemes['status'][2]}},
                totals={"marker": {"color": self.color_schemes['primary'][0]}}
            ))
            
            fig.update_layout(
                title="Investment Cost-Benefit Analysis",
                xaxis_title="Investment Categories",
                yaxis_title="Financial Impact ($)",
                **self.layout_template
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating cost-benefit analysis: {e}")
            return self._create_error_chart("Error creating cost-benefit analysis")
    
    def _create_error_chart(self, error_message: str) -> go.Figure:
        """Create error message chart"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"⚠️ {error_message}",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            font=dict(size=16, color="red"),
            showarrow=False
        )
        fig.update_layout(
            title="Chart Error",
            **self.layout_template
        )
        return fig
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty state chart"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"📊 {message}",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            font=dict(size=16, color="gray"),
            showarrow=False
        )
        fig.update_layout(
            title="No Data Available",
            **self.layout_template
        )
        return fig

# Global visualization engine instance
viz_engine = VisualizationEngine()

# Convenience functions for backward compatibility
def create_yield_chart(data: pd.DataFrame) -> go.Figure:
    """Create yield chart (convenience function)"""
    return viz_engine.create_yield_trend_chart(data)

def create_performance_metrics(metrics: Dict[str, float]) -> go.Figure:
    """Create performance metrics (convenience function)"""
    return viz_engine.create_performance_dashboard(metrics)

def create_disease_chart(disease_data: List[Dict]) -> go.Figure:
    """Create disease chart (convenience function)"""
    return viz_engine.create_disease_distribution_chart(disease_data)
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ton code principal ici
def main():
    print("✅ Script exécuté avec succès !")
    logging.info("Le script a été exécuté sans erreur.")

if __name__ == "__main__":
    main()
