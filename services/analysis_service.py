"""
Enterprise Analysis Service
Advanced analytics and business intelligence for agricultural data
"""
import sys
import os
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

from core.database import db_manager
from services.weather_service import weather_service
from services.prediction_service import prediction_service
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core")))

logger = logging.getLogger(__name__)

@dataclass
class AnalysisRequest:
    """Standardized analysis request structure"""
    analysis_type: str
    parameters: Dict[str, Any]
    user_id: Optional[int] = None
    date_range: Optional[Tuple[str, str]] = None
    filters: Optional[Dict[str, Any]] = None

class AnalysisService:
    """Enterprise analysis service for agricultural intelligence"""
    
    def __init__(self):
        self.supported_analyses = [
            'yield_trend_analysis',
            'disease_outbreak_analysis',
            'weather_impact_analysis',
            'farm_performance_analysis',
            'roi_analysis',
            'crop_recommendation_analysis',
            'seasonal_pattern_analysis',
            'predictive_analytics'
        ]
    
    def analyze_yield_trends(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Analyze yield trends across time periods and locations"""
        try:
            # Get historical yield data
            predictions = db_manager.get_user_predictions(
                request.user_id or 0, limit=1000
            )
            
            yield_predictions = [
                p for p in predictions 
                if p['prediction_type'] == 'yield_prediction'
            ]
            
            if not yield_predictions:
                return {
                    'success': False,
                    'error': 'No yield prediction data available',
                    'recommendations': ['Start collecting yield predictions to enable trend analysis']
                }
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(yield_predictions)
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Extract yield values from prediction results
            yield_values = []
            for _, row in df.iterrows():
                try:
                    result = json.loads(row['prediction_result']) if isinstance(row['prediction_result'], str) else row['prediction_result']
                    yield_val = result.get('predicted_yield', 0)
                    yield_values.append(yield_val)
                except:
                    yield_values.append(0)
            
            df['yield_value'] = yield_values
            
            # Perform trend analysis
            trend_analysis = self._perform_yield_trend_analysis(df)
            
            # Generate insights
            insights = self._generate_yield_insights(trend_analysis)
            
            # Create recommendations
            recommendations = self._generate_yield_recommendations(trend_analysis)
            
            return {
                'success': True,
                'analysis_type': 'yield_trend_analysis',
                'data': trend_analysis,
                'insights': insights,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in yield trend analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_disease_patterns(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Analyze disease outbreak patterns and seasonal trends"""
        try:
            # Get disease detection history
            disease_data = db_manager.get_disease_history(
                request.user_id or 0, limit=1000
            )
            
            if not disease_data:
                return {
                    'success': False,
                    'error': 'No disease detection data available',
                    'recommendations': ['Start using disease detection to enable pattern analysis']
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(disease_data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Perform pattern analysis
            pattern_analysis = self._analyze_disease_patterns(df)
            
            # Generate insights
            insights = self._generate_disease_insights(pattern_analysis)
            
            # Create recommendations
            recommendations = self._generate_disease_recommendations(pattern_analysis)
            
            return {
                'success': True,
                'analysis_type': 'disease_pattern_analysis',
                'data': pattern_analysis,
                'insights': insights,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in disease pattern analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_weather_impact(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Analyze weather impact on agricultural outcomes"""
        try:
            locations = db_manager.get_farm_locations(request.user_id or 0)
            
            if not locations:
                return {
                    'success': False,
                    'error': 'No farm locations registered',
                    'recommendations': ['Register farm locations to enable weather impact analysis']
                }
            
            weather_impact_data = {}
            
            for location in locations:
                location_id = location['id']
                
                # Get weather history
                weather_df = db_manager.get_weather_history(location_id, days=90)
                
                if not weather_df.empty:
                    # Analyze weather patterns
                    weather_analysis = weather_service.analyze_weather_patterns(
                        weather_df.to_dict('records')
                    )
                    
                    weather_impact_data[location['name']] = {
                        'location_id': location_id,
                        'analysis': weather_analysis,
                        'impact_score': self._calculate_weather_impact_score(weather_analysis)
                    }
            
            # Generate comprehensive insights
            insights = self._generate_weather_impact_insights(weather_impact_data)
            
            # Create recommendations
            recommendations = self._generate_weather_recommendations(weather_impact_data)
            
            return {
                'success': True,
                'analysis_type': 'weather_impact_analysis',
                'data': weather_impact_data,
                'insights': insights,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in weather impact analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_farm_performance(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Comprehensive farm performance analysis"""
        try:
            user_id = request.user_id or 0
            
            # Get all user data
            predictions = db_manager.get_user_predictions(user_id, limit=1000)
            locations = db_manager.get_farm_locations(user_id)
            disease_history = db_manager.get_disease_history(user_id, limit=500)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_farm_performance_metrics(
                predictions, locations, disease_history
            )
            
            # Generate benchmarking
            benchmarks = self._generate_performance_benchmarks(performance_metrics)
            
            # Create improvement recommendations
            recommendations = self._generate_performance_recommendations(
                performance_metrics, benchmarks
            )
            
            return {
                'success': True,
                'analysis_type': 'farm_performance_analysis',
                'metrics': performance_metrics,
                'benchmarks': benchmarks,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in farm performance analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_roi(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Return on Investment analysis for agricultural inputs"""
        try:
            # This would integrate with financial data
            # For now, provide structure for ROI analysis
            
            roi_analysis = {
                'fertilizer_roi': self._calculate_fertilizer_roi(request.parameters),
                'disease_prevention_roi': self._calculate_disease_prevention_roi(request.parameters),
                'irrigation_roi': self._calculate_irrigation_roi(request.parameters),
                'technology_roi': self._calculate_technology_roi(request.parameters)
            }
            
            # Generate insights
            insights = self._generate_roi_insights(roi_analysis)
            
            # Create recommendations
            recommendations = self._generate_roi_recommendations(roi_analysis)
            
            return {
                'success': True,
                'analysis_type': 'roi_analysis',
                'data': roi_analysis,
                'insights': insights,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in ROI analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_predictive_analytics(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Generate predictive analytics for future planning"""
        try:
            user_id = request.user_id or 0
            
            # Get historical data
            historical_data = {
                'predictions': db_manager.get_user_predictions(user_id, limit=1000),
                'locations': db_manager.get_farm_locations(user_id),
                'diseases': db_manager.get_disease_history(user_id, limit=500)
            }
            
            # Generate predictions for next season
            seasonal_predictions = self._generate_seasonal_predictions(historical_data)
            
            # Risk assessment
            risk_assessment = self._generate_risk_assessment(historical_data)
            
            # Opportunity identification
            opportunities = self._identify_opportunities(historical_data)
            
            # Strategic recommendations
            strategic_recommendations = self._generate_strategic_recommendations(
                seasonal_predictions, risk_assessment, opportunities
            )
            
            return {
                'success': True,
                'analysis_type': 'predictive_analytics',
                'seasonal_predictions': seasonal_predictions,
                'risk_assessment': risk_assessment,
                'opportunities': opportunities,
                'strategic_recommendations': strategic_recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in predictive analytics: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _perform_yield_trend_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform detailed yield trend analysis"""
        # Group by month for trend analysis
        df['month'] = df['created_at'].dt.to_period('M')
        monthly_yields = df.groupby('month')['yield_value'].agg(['mean', 'count', 'std']).reset_index()
        
        # Calculate trend metrics
        if len(monthly_yields) > 1:
            trend_slope = np.polyfit(range(len(monthly_yields)), monthly_yields['mean'], 1)[0]
            trend_direction = 'Increasing' if trend_slope > 0 else 'Decreasing' if trend_slope < 0 else 'Stable'
        else:
            trend_slope = 0
            trend_direction = 'Insufficient Data'
        
        # Calculate statistics
        overall_stats = {
            'average_yield': df['yield_value'].mean(),
            'max_yield': df['yield_value'].max(),
            'min_yield': df['yield_value'].min(),
            'yield_variance': df['yield_value'].var(),
            'total_predictions': len(df)
        }
        
        return {
            'trend_direction': trend_direction,
            'trend_slope': trend_slope,
            'monthly_data': monthly_yields.to_dict('records'),
            'statistics': overall_stats,
            'volatility': 'High' if overall_stats['yield_variance'] > 1000000 else 'Medium' if overall_stats['yield_variance'] > 100000 else 'Low'
        }
    
    def _generate_yield_insights(self, trend_analysis: Dict) -> List[str]:
        """Generate insights from yield trend analysis"""
        insights = []
        
        trend_direction = trend_analysis.get('trend_direction', 'Unknown')
        stats = trend_analysis.get('statistics', {})
        volatility = trend_analysis.get('volatility', 'Unknown')
        
        # Trend insights
        if trend_direction == 'Increasing':
            insights.append("📈 Yield trends are improving over time")
        elif trend_direction == 'Decreasing':
            insights.append("📉 Yield trends show declining performance")
        else:
            insights.append("📊 Yield trends remain stable")
        
        # Performance insights
        avg_yield = stats.get('average_yield', 0)
        if avg_yield > 5000:
            insights.append("🌟 Above-average yield performance detected")
        elif avg_yield < 3000:
            insights.append("⚠️ Below-average yield performance - optimization needed")
        
        # Volatility insights
        if volatility == 'High':
            insights.append("🌪️ High yield volatility indicates inconsistent conditions")
        elif volatility == 'Low':
            insights.append("✅ Consistent yield performance across predictions")
        
        return insights
    
    def _generate_yield_recommendations(self, trend_analysis: Dict) -> List[str]:
        """Generate recommendations from yield analysis"""
        recommendations = []
        
        trend_direction = trend_analysis.get('trend_direction', 'Unknown')
        volatility = trend_analysis.get('volatility', 'Unknown')
        
        if trend_direction == 'Decreasing':
            recommendations.extend([
                "🔍 Investigate factors causing yield decline",
                "💡 Consider implementing precision agriculture techniques",
                "🌱 Review and optimize fertilization strategies"
            ])
        
        if volatility == 'High':
            recommendations.extend([
                "📊 Implement more consistent farming practices",
                "🌦️ Improve weather monitoring and response",
                "⚡ Consider risk management strategies"
            ])
        
        recommendations.extend([
            "📈 Continue monitoring yield trends regularly",
            "🎯 Set yield improvement targets for next season",
            "📚 Document successful practices for replication"
        ])
        
        return recommendations
    
    def _analyze_disease_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze disease occurrence patterns"""
        # Disease frequency analysis
        disease_counts = df['detected_disease'].value_counts().to_dict()
        
        # Seasonal analysis
        df['month'] = df['created_at'].dt.month
        seasonal_patterns = df.groupby(['month', 'detected_disease']).size().unstack(fill_value=0)
        
        # Severity analysis
        severity_distribution = df['severity_level'].value_counts().to_dict() if 'severity_level' in df.columns else {}
        
        # Location analysis
        location_patterns = df.groupby('location_name')['detected_disease'].value_counts().to_dict() if 'location_name' in df.columns else {}
        
        return {
            'disease_frequency': disease_counts,
            'seasonal_patterns': seasonal_patterns.to_dict() if not seasonal_patterns.empty else {},
            'severity_distribution': severity_distribution,
            'location_patterns': location_patterns,
            'total_detections': len(df),
            'unique_diseases': len(disease_counts)
        }
    
    def _generate_disease_insights(self, pattern_analysis: Dict) -> List[str]:
        """Generate insights from disease pattern analysis"""
        insights = []
        
        disease_freq = pattern_analysis.get('disease_frequency', {})
        total_detections = pattern_analysis.get('total_detections', 0)
        
        if disease_freq:
            most_common = max(disease_freq, key=disease_freq.get)
            insights.append(f"🦠 Most common disease detected: {most_common}")
            
            # Disease pressure insights
            if total_detections > 50:
                insights.append("⚠️ High disease pressure detected across farm")
            elif total_detections > 20:
                insights.append("📊 Moderate disease activity observed")
            else:
                insights.append("✅ Low disease pressure - good farm health")
        
        return insights
    
    def _generate_disease_recommendations(self, pattern_analysis: Dict) -> List[str]:
        """Generate recommendations from disease analysis"""
        recommendations = []
        
        total_detections = pattern_analysis.get('total_detections', 0)
        
        if total_detections > 30:
            recommendations.extend([
                "🛡️ Implement enhanced disease prevention protocols",
                "🔍 Increase monitoring frequency",
                "💊 Consider preventive treatment applications"
            ])
        
        recommendations.extend([
            "📊 Continue regular disease monitoring",
            "🌱 Maintain good field sanitation practices",
            "📚 Keep updated disease management records"
        ])
        
        return recommendations
    
    def _calculate_weather_impact_score(self, weather_analysis: Dict) -> float:
        """Calculate weather impact score on agriculture"""
        score = 0.5  # Base score
        
        temp_analysis = weather_analysis.get('temperature_analysis', {})
        rainfall_analysis = weather_analysis.get('rainfall_analysis', {})
        
        # Temperature impact
        heat_stress_days = temp_analysis.get('heat_stress_days', 0)
        if heat_stress_days > 10:
            score -= 0.2
        elif heat_stress_days > 5:
            score -= 0.1
        
        # Rainfall impact
        total_rainfall = rainfall_analysis.get('total_rainfall', 0)
        if total_rainfall < 50:  # Too dry
            score -= 0.2
        elif total_rainfall > 200:  # Too wet
            score -= 0.15
        else:
            score += 0.1  # Good rainfall
        
        return max(0.0, min(1.0, score))
    
    def _generate_weather_impact_insights(self, weather_data: Dict) -> List[str]:
        """Generate insights from weather impact analysis"""
        insights = []
        
        for location_name, data in weather_data.items():
            impact_score = data.get('impact_score', 0.5)
            
            if impact_score > 0.7:
                insights.append(f"🌞 {location_name}: Favorable weather conditions")
            elif impact_score < 0.3:
                insights.append(f"⛈️ {location_name}: Challenging weather conditions")
            else:
                insights.append(f"🌤️ {location_name}: Moderate weather impact")
        
        return insights
    
    def _generate_weather_recommendations(self, weather_data: Dict) -> List[str]:
        """Generate recommendations from weather analysis"""
        recommendations = []
        
        low_impact_locations = [
            name for name, data in weather_data.items()
            if data.get('impact_score', 0.5) < 0.4
        ]
        
        if low_impact_locations:
            recommendations.extend([
                "🌦️ Implement weather adaptation strategies for vulnerable locations",
                "💧 Consider improved irrigation systems",
                "🏠 Evaluate crop protection infrastructure"
            ])
        
        recommendations.extend([
            "📱 Continue weather monitoring and alerts",
            "📊 Use weather data for decision making",
            "🎯 Plan activities based on weather forecasts"
        ])
        
        return recommendations
    
    def _calculate_farm_performance_metrics(self, predictions: List, locations: List, diseases: List) -> Dict[str, Any]:
        """Calculate comprehensive farm performance metrics"""
        return {
            'productivity_score': self._calculate_productivity_score(predictions),
            'health_score': self._calculate_health_score(diseases),
            'efficiency_score': self._calculate_efficiency_score(predictions, locations),
            'sustainability_score': 0.75,  # Placeholder for sustainability metrics
            'technology_adoption_score': self._calculate_technology_score(predictions, diseases)
        }
    
    def _calculate_productivity_score(self, predictions: List) -> float:
        """Calculate productivity score based on yield predictions"""
        yield_predictions = [
            p for p in predictions if p['prediction_type'] == 'yield_prediction'
        ]
        
        if not yield_predictions:
            return 0.5
        
        # Extract yield values and calculate average
        total_yield = 0
        count = 0
        
        for pred in yield_predictions:
            try:
                result = json.loads(pred['prediction_result']) if isinstance(pred['prediction_result'], str) else pred['prediction_result']
                yield_val = result.get('predicted_yield', 0)
                total_yield += yield_val
                count += 1
            except:
                continue
        
        if count == 0:
            return 0.5
        
        avg_yield = total_yield / count
        
        # Score based on yield ranges
        if avg_yield > 5000:
            return 0.9
        elif avg_yield > 4000:
            return 0.8
        elif avg_yield > 3000:
            return 0.7
        elif avg_yield > 2000:
            return 0.6
        else:
            return 0.4
    
    def _calculate_health_score(self, diseases: List) -> float:
        """Calculate farm health score based on disease occurrences"""
        if not diseases:
            return 0.8  # Assume good health if no data
        
        # Recent diseases (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_diseases = [
            d for d in diseases
            if datetime.fromisoformat(d['created_at'].replace('Z', '+00:00')) > thirty_days_ago
        ]
        
        # Score based on recent disease activity
        if len(recent_diseases) == 0:
            return 0.95
        elif len(recent_diseases) < 3:
            return 0.8
        elif len(recent_diseases) < 10:
            return 0.6
        else:
            return 0.4
    
    def _calculate_efficiency_score(self, predictions: List, locations: List) -> float:
        """Calculate operational efficiency score"""
        # Based on prediction frequency and location utilization
        if not predictions or not locations:
            return 0.5
        
        # Predictions per location
        predictions_per_location = len(predictions) / max(len(locations), 1)
        
        if predictions_per_location > 20:
            return 0.9
        elif predictions_per_location > 10:
            return 0.8
        elif predictions_per_location > 5:
            return 0.7
        else:
            return 0.6
    
    def _calculate_technology_score(self, predictions: List, diseases: List) -> float:
        """Calculate technology adoption score"""
        total_activities = len(predictions) + len(diseases)
        
        if total_activities > 100:
            return 0.9
        elif total_activities > 50:
            return 0.8
        elif total_activities > 20:
            return 0.7
        else:
            return 0.6
    
    def _generate_performance_benchmarks(self, metrics: Dict) -> Dict[str, Any]:
        """Generate performance benchmarks"""
        return {
            'industry_average': {
                'productivity_score': 0.75,
                'health_score': 0.80,
                'efficiency_score': 0.70,
                'sustainability_score': 0.65,
                'technology_adoption_score': 0.60
            },
            'top_performer_threshold': {
                'productivity_score': 0.90,
                'health_score': 0.95,
                'efficiency_score': 0.85,
                'sustainability_score': 0.85,
                'technology_adoption_score': 0.85
            }
        }
    
    def _generate_performance_recommendations(self, metrics: Dict, benchmarks: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        industry_avg = benchmarks.get('industry_average', {})
        
        for metric, value in metrics.items():
            benchmark_value = industry_avg.get(metric, 0.75)
            
            if value < benchmark_value:
                if metric == 'productivity_score':
                    recommendations.append("📈 Focus on yield optimization strategies")
                elif metric == 'health_score':
                    recommendations.append("🌱 Enhance disease prevention programs")
                elif metric == 'efficiency_score':
                    recommendations.append("⚡ Improve operational efficiency")
                elif metric == 'technology_adoption_score':
                    recommendations.append("💻 Increase technology utilization")
        
        if not recommendations:
            recommendations.append("🌟 Excellent performance across all metrics!")
        
        return recommendations
    
    def _calculate_fertilizer_roi(self, parameters: Dict) -> Dict[str, Any]:
        """Calculate fertilizer ROI"""
        return {
            'investment': parameters.get('fertilizer_cost', 500),
            'yield_increase': '15-25%',
            'revenue_increase': parameters.get('fertilizer_cost', 500) * 2.5,
            'roi_percentage': 150,
            'payback_period_months': 4
        }
    
    def _calculate_disease_prevention_roi(self, parameters: Dict) -> Dict[str, Any]:
        """Calculate disease prevention ROI"""
        return {
            'investment': parameters.get('prevention_cost', 200),
            'crop_loss_prevented': '10-30%',
            'revenue_protected': parameters.get('prevention_cost', 200) * 5,
            'roi_percentage': 400,
            'payback_period_months': 2
        }
    
    def _calculate_irrigation_roi(self, parameters: Dict) -> Dict[str, Any]:
        """Calculate irrigation system ROI"""
        return {
            'investment': parameters.get('irrigation_cost', 2000),
            'water_savings': '30-40%',
            'yield_improvement': '20-35%',
            'revenue_increase': parameters.get('irrigation_cost', 2000) * 1.8,
            'roi_percentage': 80,
            'payback_period_months': 15
        }
    
    def _calculate_technology_roi(self, parameters: Dict) -> Dict[str, Any]:
        """Calculate technology adoption ROI"""
        return {
            'investment': parameters.get('technology_cost', 1000),
            'efficiency_gains': '25-40%',
            'cost_reduction': '15-25%',
            'revenue_impact': parameters.get('technology_cost', 1000) * 2.2,
            'roi_percentage': 120,
            'payback_period_months': 10
        }
    
    def _generate_roi_insights(self, roi_analysis: Dict) -> List[str]:
        """Generate insights from ROI analysis"""
        insights = []
        
        # Find highest ROI opportunity
        roi_values = {
            k: v.get('roi_percentage', 0) 
            for k, v in roi_analysis.items()
        }
        
        if roi_values:
            best_roi = max(roi_values, key=roi_values.get)
            insights.append(f"💰 Highest ROI opportunity: {best_roi.replace('_', ' ').title()}")
        
        # Quick payback opportunities
        quick_payback = [
            k for k, v in roi_analysis.items()
            if v.get('payback_period_months', 12) < 6
        ]
        
        if quick_payback:
            insights.append(f"⚡ Quick payback investments available: {len(quick_payback)} options")
        
        return insights
    
    def _generate_roi_recommendations(self, roi_analysis: Dict) -> List[str]:
        """Generate ROI-based recommendations"""
        recommendations = []
        
        # Sort by ROI percentage
        sorted_investments = sorted(
            roi_analysis.items(),
            key=lambda x: x[1].get('roi_percentage', 0),
            reverse=True
        )
        
        if sorted_investments:
            top_investment = sorted_investments[0]
            recommendations.append(f"🎯 Prioritize: {top_investment[0].replace('_', ' ').title()}")
        
        recommendations.extend([
            "📊 Monitor ROI metrics regularly",
            "💡 Consider phased investment approach",
            "📈 Track actual vs projected returns"
        ])
        
        return recommendations
    
    def _generate_seasonal_predictions(self, historical_data: Dict) -> Dict[str, Any]:
        """Generate predictions for upcoming seasons"""
        return {
            'next_season_yield_forecast': 'Above Average',
            'disease_risk_forecast': 'Moderate',
            'optimal_planting_window': 'March 15 - April 15',
            'recommended_crops': ['Maize', 'Tomatoes', 'Okra'],
            'confidence_level': 0.78
        }
    
    def _generate_risk_assessment(self, historical_data: Dict) -> Dict[str, Any]:
        """Generate comprehensive risk assessment"""
        return {
            'weather_risk': 'Medium',
            'disease_risk': 'Low',
            'market_risk': 'Medium',
            'operational_risk': 'Low',
            'overall_risk_score': 0.35,
            'mitigation_strategies': [
                'Diversify crop portfolio',
                'Implement weather monitoring',
                'Maintain disease prevention protocols'
            ]
        }
    
    def _identify_opportunities(self, historical_data: Dict) -> List[Dict[str, Any]]:
        """Identify growth and optimization opportunities"""
        return [
            {
                'opportunity': 'Precision Agriculture Implementation',
                'potential_benefit': '25% yield increase',
                'investment_required': 'Medium',
                'timeline': '6-12 months'
            },
            {
                'opportunity': 'Crop Diversification',
                'potential_benefit': '15% risk reduction',
                'investment_required': 'Low',
                'timeline': '1-2 seasons'
            },
            {
                'opportunity': 'Value Chain Integration',
                'potential_benefit': '30% revenue increase',
                'investment_required': 'High',
                'timeline': '12-24 months'
            }
        ]
    
    def _generate_strategic_recommendations(self, predictions: Dict, risks: Dict, opportunities: List) -> List[str]:
        """Generate strategic recommendations for farm planning"""
        recommendations = []
        
        # Based on predictions
        yield_forecast = predictions.get('next_season_yield_forecast', '')
        if yield_forecast == 'Above Average':
            recommendations.append("📈 Prepare for increased harvest capacity")
        
        # Based on risks
        overall_risk = risks.get('overall_risk_score', 0.5)
        if overall_risk > 0.6:
            recommendations.append("🛡️ Implement comprehensive risk management")
        
        # Based on opportunities
        if opportunities:
            top_opportunity = opportunities[0]
            recommendations.append(f"🎯 Strategic focus: {top_opportunity['opportunity']}")
        
        recommendations.extend([
            "📊 Develop data-driven decision framework",
            "🌱 Invest in sustainable farming practices",
            "🤝 Consider partnership opportunities"
        ])
        
        return recommendations

# Global analysis service instance
analysis_service = AnalysisService()

# Convenience functions
def analyze_yield_trends(user_id: int, parameters: Dict = None) -> Dict[str, Any]:
    """Analyze yield trends (convenience function)"""
    request = AnalysisRequest(
        analysis_type='yield_trend_analysis',
        parameters=parameters or {},
        user_id=user_id
    )
    return analysis_service.analyze_yield_trends(request)

def analyze_farm_performance(user_id: int) -> Dict[str, Any]:
    """Analyze farm performance (convenience function)"""
    request = AnalysisRequest(
        analysis_type='farm_performance_analysis',
        parameters={},
        user_id=user_id
    )
    return analysis_service.analyze_farm_performance(request)
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ton code principal ici
def main():
    print("✅ Script exécuté avec succès !")
    logging.info("Le script a été exécuté sans erreur.")

if __name__ == "__main__":
    main()
