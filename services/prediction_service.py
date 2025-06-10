"""
Enterprise Prediction Service
Centralizes all prediction logic with advanced analytics
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

from models.ml_models import model_manager
from services.weather_service import weather_service
from core.database import db_manager

logger = logging.getLogger(__name__)

@dataclass
class PredictionRequest:
    """Standardized prediction request structure"""
    user_id: int
    prediction_type: str
    input_data: Dict[str, Any]
    location: Optional[Dict[str, float]] = None
    timestamp: Optional[str] = None

@dataclass
class PredictionResult:
    """Standardized prediction result structure"""
    success: bool
    prediction_id: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    recommendations: Optional[List[str]] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None

class PredictionService:
    """Enterprise prediction service with integrated analytics"""
    
    def __init__(self):
        self.supported_predictions = [
            'yield_prediction',
            'disease_detection',
            'fertilizer_recommendation',
            'weather_forecast',
            'pest_risk_assessment',
            'irrigation_scheduling'
        ]
        self.prediction_history = []
    
    def predict_crop_yield(self, request: PredictionRequest) -> PredictionResult:
        """Advanced crop yield prediction with weather integration"""
        try:
            # Validate input
            if not self._validate_yield_input(request.input_data):
                return PredictionResult(
                    success=False,
                    error="Invalid input data for yield prediction"
                )
            
            # Enhance input with weather data if location provided
            enhanced_input = request.input_data.copy()
            if request.location:
                weather_data = self._get_weather_context(request.location)
                enhanced_input.update(weather_data)
            
            # Get base prediction from ML model
            ml_result = model_manager.predict_yield(enhanced_input)
            
            if 'error' in ml_result:
                return PredictionResult(
                    success=False,
                    error=ml_result['error']
                )
            
            # Enhance prediction with advanced analytics
            enhanced_result = self._enhance_yield_prediction(ml_result, enhanced_input)
            
            # Generate recommendations
            recommendations = self._generate_yield_recommendations(enhanced_result, enhanced_input)
            
            # Save prediction to database
            prediction_id = db_manager.save_prediction(
                user_id=request.user_id,
                prediction_type='yield_prediction',
                input_data=enhanced_input,
                result=enhanced_result,
                confidence=enhanced_result.get('confidence')
            )
            
            return PredictionResult(
                success=True,
                prediction_id=prediction_id,
                result=enhanced_result,
                confidence=enhanced_result.get('confidence'),
                recommendations=recommendations,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in yield prediction: {e}")
            return PredictionResult(
                success=False,
                error=str(e)
            )
    
    def detect_plant_disease(self, request: PredictionRequest) -> PredictionResult:
        """Advanced plant disease detection with treatment recommendations"""
        try:
            if 'image' not in request.input_data:
                return PredictionResult(
                    success=False,
                    error="Image data required for disease detection"
                )
            
            # Get disease detection result
            from models.disease_detector import disease_detector
            detection_result = disease_detector.detect_disease(
                request.input_data['image'],
                return_top_k=3
            )
            
            if not detection_result.get('success'):
                return PredictionResult(
                    success=False,
                    error=detection_result.get('error', 'Disease detection failed')
                )
            
            # Enhance with environmental context
            if request.location:
                environmental_context = self._get_environmental_disease_context(request.location)
                detection_result['environmental_factors'] = environmental_context
            
            # Generate comprehensive recommendations
            recommendations = self._generate_disease_recommendations(detection_result)
            
            # Save to database
            prediction_id = db_manager.save_prediction(
                user_id=request.user_id,
                prediction_type='disease_detection',
                input_data={'image_processed': True, 'location': request.location},
                result=detection_result,
                confidence=detection_result.get('primary_diagnosis', {}).get('confidence')
            )
            
            return PredictionResult(
                success=True,
                prediction_id=prediction_id,
                result=detection_result,
                confidence=detection_result.get('primary_diagnosis', {}).get('confidence'),
                recommendations=recommendations,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in disease detection: {e}")
            return PredictionResult(
                success=False,
                error=str(e)
            )
    
    def recommend_fertilizer(self, request: PredictionRequest) -> PredictionResult:
        """Advanced fertilizer recommendation with economic analysis"""
        try:
            # Validate input
            if not self._validate_fertilizer_input(request.input_data):
                return PredictionResult(
                    success=False,
                    error="Invalid input data for fertilizer recommendation"
                )
            
            # Get base recommendation
            recommendation_result = model_manager.recommend_fertilizer(request.input_data)
            
            if 'error' in recommendation_result:
                return PredictionResult(
                    success=False,
                    error=recommendation_result['error']
                )
            
            # Enhance with economic analysis
            economic_analysis = self._calculate_fertilizer_economics(
                recommendation_result, request.input_data
            )
            recommendation_result['economic_analysis'] = economic_analysis
            
            # Add timing recommendations
            timing_advice = self._generate_application_timing(request.input_data)
            recommendation_result['timing_recommendations'] = timing_advice
            
            # Generate comprehensive recommendations
            recommendations = self._generate_fertilizer_recommendations(
                recommendation_result, request.input_data
            )
            
            # Save to database
            prediction_id = db_manager.save_prediction(
                user_id=request.user_id,
                prediction_type='fertilizer_recommendation',
                input_data=request.input_data,
                result=recommendation_result
            )
            
            return PredictionResult(
                success=True,
                prediction_id=prediction_id,
                result=recommendation_result,
                recommendations=recommendations,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in fertilizer recommendation: {e}")
            return PredictionResult(
                success=False,
                error=str(e)
            )
    
    def assess_pest_risk(self, request: PredictionRequest) -> PredictionResult:
        """Assess pest risk based on environmental conditions"""
        try:
            if not request.location:
                return PredictionResult(
                    success=False,
                    error="Location required for pest risk assessment"
                )
            
            # Get weather context
            weather_data = weather_service.get_current_weather(
                request.location['latitude'],
                request.location['longitude']
            )
            
            if 'error' in weather_data:
                return PredictionResult(
                    success=False,
                    error=f"Weather data unavailable: {weather_data['error']}"
                )
            
            # Calculate pest risk factors
            risk_assessment = self._calculate_pest_risk(weather_data, request.input_data)
            
            # Generate recommendations
            recommendations = self._generate_pest_recommendations(risk_assessment)
            
            # Save to database
            prediction_id = db_manager.save_prediction(
                user_id=request.user_id,
                prediction_type='pest_risk_assessment',
                input_data=request.input_data,
                result=risk_assessment
            )
            
            return PredictionResult(
                success=True,
                prediction_id=prediction_id,
                result=risk_assessment,
                recommendations=recommendations,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in pest risk assessment: {e}")
            return PredictionResult(
                success=False,
                error=str(e)
            )
    
    def schedule_irrigation(self, request: PredictionRequest) -> PredictionResult:
        """Generate irrigation schedule based on crop needs and weather"""
        try:
            if not request.location:
                return PredictionResult(
                    success=False,
                    error="Location required for irrigation scheduling"
                )
            
            # Get weather forecast
            forecast = weather_service.get_weather_forecast(
                request.location['latitude'],
                request.location['longitude'],
                days=7
            )
            
            if 'error' in forecast:
                return PredictionResult(
                    success=False,
                    error=f"Weather forecast unavailable: {forecast['error']}"
                )
            
            # Calculate irrigation needs
            irrigation_schedule = self._calculate_irrigation_schedule(
                forecast, request.input_data
            )
            
            # Generate recommendations
            recommendations = self._generate_irrigation_recommendations(irrigation_schedule)
            
            # Save to database
            prediction_id = db_manager.save_prediction(
                user_id=request.user_id,
                prediction_type='irrigation_scheduling',
                input_data=request.input_data,
                result=irrigation_schedule
            )
            
            return PredictionResult(
                success=True,
                prediction_id=prediction_id,
                result=irrigation_schedule,
                recommendations=recommendations,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error in irrigation scheduling: {e}")
            return PredictionResult(
                success=False,
                error=str(e)
            )
    
    def get_prediction_history(self, user_id: int, 
                             prediction_type: str = None, limit: int = 50) -> List[Dict]:
        """Get user's prediction history with analytics"""
        try:
            predictions = db_manager.get_user_predictions(user_id, limit)
            
            if prediction_type:
                predictions = [p for p in predictions if p['prediction_type'] == prediction_type]
            
            # Add analytics
            for prediction in predictions:
                prediction['analytics'] = self._calculate_prediction_analytics(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error fetching prediction history: {e}")
            return []
    
    def _validate_yield_input(self, input_data: Dict) -> bool:
        """Validate yield prediction input"""
        required_fields = ['crop_type', 'soil_type', 'temperature', 'humidity']
        return all(field in input_data for field in required_fields)
    
    def _validate_fertilizer_input(self, input_data: Dict) -> bool:
        """Validate fertilizer recommendation input"""
        required_fields = ['crop_type', 'soil_type', 'ph', 'nitrogen', 'phosphorus', 'potassium']
        return all(field in input_data for field in required_fields)
    
    def _get_weather_context(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Get relevant weather data for predictions"""
        try:
            current_weather = weather_service.get_current_weather(
                location['latitude'], location['longitude']
            )
            
            if 'error' in current_weather:
                return {}
            
            return {
                'current_temperature': current_weather.get('temperature', 0),
                'current_humidity': current_weather.get('humidity', 0),
                'current_pressure': current_weather.get('pressure', 0),
                'current_wind_speed': current_weather.get('wind_speed', 0)
            }
        except:
            return {}
    
    def _enhance_yield_prediction(self, base_result: Dict, input_data: Dict) -> Dict[str, Any]:
        """Enhance yield prediction with additional analytics"""
        enhanced = base_result.copy()
        
        # Add yield classification
        predicted_yield = enhanced.get('predicted_yield', 0)
        enhanced['yield_classification'] = self._classify_yield(predicted_yield)
        
        # Add factors analysis
        enhanced['limiting_factors'] = self._identify_limiting_factors(input_data)
        
        # Add optimization suggestions
        enhanced['optimization_potential'] = self._calculate_optimization_potential(input_data)
        
        return enhanced
    
    def _classify_yield(self, yield_value: float) -> str:
        """Classify yield into categories"""
        if yield_value > 5000:
            return "Excellent"
        elif yield_value > 4000:
            return "Good"
        elif yield_value > 3000:
            return "Average"
        elif yield_value > 2000:
            return "Below Average"
        else:
            return "Poor"
    
    def _identify_limiting_factors(self, input_data: Dict) -> List[str]:
        """Identify factors that might limit yield"""
        factors = []
        
        if input_data.get('ph', 7) < 6.0:
            factors.append("Soil pH too acidic")
        elif input_data.get('ph', 7) > 8.0:
            factors.append("Soil pH too alkaline")
        
        if input_data.get('nitrogen', 0) < 30:
            factors.append("Low nitrogen levels")
        
        if input_data.get('phosphorus', 0) < 15:
            factors.append("Low phosphorus levels")
        
        if input_data.get('potassium', 0) < 150:
            factors.append("Low potassium levels")
        
        return factors
    
    def _calculate_optimization_potential(self, input_data: Dict) -> Dict[str, Any]:
        """Calculate potential for yield optimization"""
        return {
            'nutrition_optimization': 0.85 if input_data.get('nitrogen', 0) < 50 else 0.95,
            'water_management': 0.80,
            'pest_control': 0.90,
            'overall_potential': 0.85
        }
    
    def _generate_yield_recommendations(self, result: Dict, input_data: Dict) -> List[str]:
        """Generate actionable yield improvement recommendations"""
        recommendations = []
        
        # Based on limiting factors
        limiting_factors = result.get('limiting_factors', [])
        for factor in limiting_factors:
            if "pH" in factor:
                recommendations.append("🧪 Consider soil pH amendment")
            elif "nitrogen" in factor.lower():
                recommendations.append("💚 Apply nitrogen-rich fertilizer")
            elif "phosphorus" in factor.lower():
                recommendations.append("🟣 Increase phosphorus application")
            elif "potassium" in factor.lower():
                recommendations.append("🟡 Add potassium supplement")
        
        # Based on yield classification
        classification = result.get('yield_classification', '')
        if classification in ['Poor', 'Below Average']:
            recommendations.append("📈 Consider crop variety improvement")
            recommendations.append("🌱 Implement precision agriculture techniques")
        
        # Weather-based recommendations
        if input_data.get('current_humidity', 0) > 80:
            recommendations.append("💨 Improve field ventilation to reduce disease risk")
        
        return recommendations
    
    def _get_environmental_disease_context(self, location: Dict[str, float]) -> Dict[str, Any]:
        """Get environmental context for disease detection"""
        try:
            weather_data = weather_service.get_current_weather(
                location['latitude'], location['longitude']
            )
            
            return {
                'temperature': weather_data.get('temperature', 0),
                'humidity': weather_data.get('humidity', 0),
                'disease_risk_factors': self._assess_disease_risk_factors(weather_data)
            }
        except:
            return {}
    
    def _assess_disease_risk_factors(self, weather_data: Dict) -> List[str]:
        """Assess environmental disease risk factors"""
        risk_factors = []
        
        humidity = weather_data.get('humidity', 0)
        temperature = weather_data.get('temperature', 0)
        
        if humidity > 80:
            risk_factors.append("High humidity favors fungal diseases")
        
        if 20 <= temperature <= 30:
            risk_factors.append("Optimal temperature range for many pathogens")
        
        return risk_factors
    
    def _generate_disease_recommendations(self, detection_result: Dict) -> List[str]:
        """Generate comprehensive disease management recommendations"""
        recommendations = []
        
        primary_diagnosis = detection_result.get('primary_diagnosis', {})
        confidence = primary_diagnosis.get('confidence', 0)
        
        if confidence > 0.8:
            recommendations.append("🎯 High confidence detection - proceed with treatment")
            recommendations.extend(primary_diagnosis.get('treatment', [])[:3])
        elif confidence > 0.6:
            recommendations.append("⚠️ Moderate confidence - consider additional testing")
        else:
            recommendations.append("❓ Low confidence - retake photo with better lighting")
        
        # Prevention recommendations
        recommendations.extend([
            "🛡️ Implement preventive measures",
            "📊 Monitor plant health regularly",
            "📸 Document treatment progress"
        ])
        
        return recommendations
    
    def _calculate_fertilizer_economics(self, recommendation: Dict, input_data: Dict) -> Dict[str, Any]:
        """Calculate economic analysis for fertilizer recommendation"""
        # Simplified economic calculation
        base_cost = 100  # Base cost per hectare
        
        fertilizer_type = recommendation.get('recommended_fertilizer', '')
        
        cost_multipliers = {
            'Urea': 1.0,
            'NPK': 1.2,
            'Organic': 1.5,
            'Specialty': 2.0
        }
        
        multiplier = 1.0
        for fert_type, mult in cost_multipliers.items():
            if fert_type.lower() in fertilizer_type.lower():
                multiplier = mult
                break
        
        estimated_cost = base_cost * multiplier
        
        return {
            'estimated_cost_per_hectare': estimated_cost,
            'expected_yield_increase': '15-25%',
            'roi_estimate': 2.5,
            'cost_effectiveness': 'High' if multiplier <= 1.2 else 'Medium'
        }
    
    def _generate_application_timing(self, input_data: Dict) -> List[str]:
        """Generate fertilizer application timing recommendations"""
        crop_type = input_data.get('crop_type', '').lower()
        growth_stage = input_data.get('growth_stage', '').lower()
        
        timing_advice = []
        
        if growth_stage == 'germination':
            timing_advice.append("Apply phosphorus-rich fertilizer for root development")
        elif growth_stage == 'vegetative':
            timing_advice.append("Apply nitrogen-rich fertilizer for leaf growth")
        elif growth_stage == 'flowering':
            timing_advice.append("Reduce nitrogen, increase phosphorus and potassium")
        elif growth_stage == 'fruiting':
            timing_advice.append("Focus on potassium for fruit development")
        
        timing_advice.extend([
            "Apply in early morning or late evening",
            "Ensure soil moisture before application",
            "Split applications for better nutrient uptake"
        ])
        
        return timing_advice
    
    def _generate_fertilizer_recommendations(self, result: Dict, input_data: Dict) -> List[str]:
        """Generate comprehensive fertilizer recommendations"""
        recommendations = []
        
        fertilizer = result.get('recommended_fertilizer', '')
        recommendations.append(f"📋 Recommended: {fertilizer}")
        
        # Economic recommendations
        economics = result.get('economic_analysis', {})
        if economics.get('cost_effectiveness') == 'High':
            recommendations.append("💰 Cost-effective option for maximum ROI")
        
        # Timing recommendations
        timing = result.get('timing_recommendations', [])
        recommendations.extend(timing[:2])
        
        # Application recommendations
        recommendations.extend(result.get('application_advice', [])[:2])
        
        return recommendations
    
    def _calculate_pest_risk(self, weather_data: Dict, input_data: Dict) -> Dict[str, Any]:
        """Calculate pest risk based on environmental conditions"""
        temperature = weather_data.get('temperature', 0)
        humidity = weather_data.get('humidity', 0)
        
        # Simplified pest risk calculation
        risk_score = 0
        risk_factors = []
        
        if 25 <= temperature <= 35:
            risk_score += 30
            risk_factors.append("Optimal temperature for pest activity")
        
        if humidity > 70:
            risk_score += 25
            risk_factors.append("High humidity favors pest breeding")
        
        if input_data.get('crop_type', '').lower() in ['tomato', 'maize']:
            risk_score += 20
            risk_factors.append("Crop type susceptible to common pests")
        
        risk_level = "Low"
        if risk_score > 60:
            risk_level = "High"
        elif risk_score > 30:
            risk_level = "Medium"
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'primary_pests': self._identify_likely_pests(input_data, weather_data)
        }
    
    def _identify_likely_pests(self, input_data: Dict, weather_data: Dict) -> List[str]:
        """Identify likely pests based on conditions"""
        crop_type = input_data.get('crop_type', '').lower()
        temperature = weather_data.get('temperature', 0)
        
        pest_map = {
            'tomato': ['Aphids', 'Whiteflies', 'Hornworms'],
            'maize': ['Corn Borers', 'Armyworms', 'Cutworms'],
            'rice': ['Rice Borers', 'Brown Planthoppers', 'Leaf Folders']
        }
        
        return pest_map.get(crop_type, ['General Pests'])
    
    def _generate_pest_recommendations(self, risk_assessment: Dict) -> List[str]:
        """Generate pest management recommendations"""
        recommendations = []
        risk_level = risk_assessment.get('risk_level', 'Low')
        
        if risk_level == 'High':
            recommendations.extend([
                "🚨 High pest risk - implement immediate monitoring",
                "🔍 Inspect crops daily for pest signs",
                "💊 Consider preventive treatment if necessary"
            ])
        elif risk_level == 'Medium':
            recommendations.extend([
                "⚠️ Moderate pest risk - increase monitoring frequency",
                "🌱 Use integrated pest management practices"
            ])
        else:
            recommendations.extend([
                "✅ Low pest risk - maintain regular monitoring",
                "🌿 Continue preventive measures"
            ])
        
        # Add specific pest recommendations
        primary_pests = risk_assessment.get('primary_pests', [])
        for pest in primary_pests[:2]:
            recommendations.append(f"🐛 Monitor for {pest}")
        
        return recommendations
    
    def _calculate_irrigation_schedule(self, forecast: Dict, input_data: Dict) -> Dict[str, Any]:
        """Calculate irrigation schedule based on weather forecast"""
        forecast_data = forecast.get('forecast', [])
        
        irrigation_schedule = []
        for day in forecast_data:
            date = day.get('date')
            rainfall = day.get('rainfall', 0)
            temperature = day.get('temperature_max', 0)
            
            irrigation_needed = False
            irrigation_amount = 0
            
            if rainfall < 5:  # Less than 5mm rain
                if temperature > 30:
                    irrigation_needed = True
                    irrigation_amount = 25  # mm
                elif temperature > 25:
                    irrigation_needed = True
                    irrigation_amount = 15  # mm
            
            irrigation_schedule.append({
                'date': date,
                'irrigation_needed': irrigation_needed,
                'amount_mm': irrigation_amount,
                'reason': f"Rainfall: {rainfall}mm, Max temp: {temperature}°C"
            })
        
        return {
            'schedule': irrigation_schedule,
            'total_irrigation_needed': sum(day['amount_mm'] for day in irrigation_schedule),
            'irrigation_days': len([day for day in irrigation_schedule if day['irrigation_needed']])
        }
    
    def _generate_irrigation_recommendations(self, schedule: Dict) -> List[str]:
        """Generate irrigation recommendations"""
        recommendations = []
        
        irrigation_days = schedule.get('irrigation_days', 0)
        total_amount = schedule.get('total_irrigation_needed', 0)
        
        recommendations.append(f"📊 {irrigation_days} irrigation days needed this week")
        recommendations.append(f"💧 Total irrigation requirement: {total_amount}mm")
        
        if irrigation_days > 5:
            recommendations.append("⚠️ High irrigation demand - ensure water availability")
        elif irrigation_days == 0:
            recommendations.append("✅ No irrigation needed - adequate rainfall expected")
        
        recommendations.extend([
            "🕐 Irrigate early morning or evening to reduce evaporation",
            "💧 Use drip irrigation for water efficiency",
            "📏 Monitor soil moisture levels"
        ])
        
        return recommendations
    
    def _calculate_prediction_analytics(self, prediction: Dict) -> Dict[str, Any]:
        """Calculate analytics for individual predictions"""
        created_at = prediction.get('created_at', '')
        prediction_type = prediction.get('prediction_type', '')
        
        # Calculate days since prediction
        try:
            pred_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_ago = (datetime.now() - pred_date).days
        except:
            days_ago = 0
        
        return {
            'days_since_prediction': days_ago,
            'prediction_category': prediction_type.replace('_', ' ').title(),
            'accuracy_tracking': 'Available' if days_ago > 7 else 'Pending'
        }

# Global prediction service instance
prediction_service = PredictionService()

# Convenience functions for backward compatibility
def predict_yield(input_data: Dict, user_id: int = 1) -> Dict[str, Any]:
    """Predict yield (backward compatibility)"""
    request = PredictionRequest(
        user_id=user_id,
        prediction_type='yield_prediction',
        input_data=input_data
    )
    result = prediction_service.predict_crop_yield(request)
    return result.__dict__

def detect_plant_disease(image_data, user_id: int = 1) -> Dict[str, Any]:
    """Detect disease (backward compatibility)"""
    request = PredictionRequest(
        user_id=user_id,
        prediction_type='disease_detection',
        input_data={'image': image_data}
    )
    result = prediction_service.detect_plant_disease(request)
    return result.__dict__
