
import json
import re
from typing import Dict, List, Any
from datetime import datetime
import random

class VoiceAssistant:
    def __init__(self):
        self.responses = {
            'greeting': [
                "Hello! I'm your agricultural AI assistant. How can I help you today?",
                "Good day! I'm here to help with your farming questions.",
                "Welcome! I'm your smart farming companion. What would you like to know?"
            ],
            'weather': [
                "Based on current conditions, here's what I recommend for your crops...",
                "The weather forecast suggests the following actions...",
                "Current weather conditions indicate..."
            ],
            'disease': [
                "I've analyzed your crop symptoms. Here's my diagnosis...",
                "Based on the image analysis, your crops show signs of...",
                "The disease detection system identifies..."
            ],
            'irrigation': [
                "Your irrigation schedule should be adjusted as follows...",
                "Based on soil moisture and weather data...",
                "I recommend the following irrigation plan..."
            ],
            'fertilizer': [
                "Your soil analysis shows the following nutrient needs...",
                "Based on your crop type and growth stage...",
                "I recommend this fertilizer application plan..."
            ]
        }
        
        self.knowledge_base = {
            'crops': {
                'wheat': {
                    'planting_season': 'Fall/Winter',
                    'harvest_time': '90-120 days',
                    'water_needs': 'Moderate',
                    'common_diseases': ['rust', 'blight', 'smut'],
                    'optimal_temp': '15-25°C'
                },
                'corn': {
                    'planting_season': 'Spring',
                    'harvest_time': '100-130 days',
                    'water_needs': 'High',
                    'common_diseases': ['corn borer', 'rust', 'blight'],
                    'optimal_temp': '20-30°C'
                },
                'rice': {
                    'planting_season': 'Spring/Summer',
                    'harvest_time': '120-150 days',
                    'water_needs': 'Very High',
                    'common_diseases': ['blast', 'blight', 'sheath rot'],
                    'optimal_temp': '25-35°C'
                }
            },
            'diseases': {
                'rust': {
                    'symptoms': 'Orange/brown spots on leaves',
                    'treatment': 'Fungicide application, crop rotation',
                    'prevention': 'Resistant varieties, proper spacing'
                },
                'blight': {
                    'symptoms': 'Dark spots, wilting leaves',
                    'treatment': 'Remove affected plants, fungicide',
                    'prevention': 'Good air circulation, avoid overhead watering'
                }
            }
        }
    
    def process_voice_command(self, text: str) -> Dict[str, Any]:
        """Process voice command and return appropriate response"""
        text = text.lower().strip()
        
        # Intent recognition (simple keyword-based)
        intent = self._classify_intent(text)
        
        response_data = {
            'intent': intent,
            'text_response': '',
            'voice_response': '',
            'actions': [],
            'data': {}
        }
        
        if intent == 'greeting':
            response_data['text_response'] = random.choice(self.responses['greeting'])
            
        elif intent == 'weather_inquiry':
            response_data.update(self._handle_weather_inquiry(text))
            
        elif intent == 'disease_diagnosis':
            response_data.update(self._handle_disease_inquiry(text))
            
        elif intent == 'irrigation_advice':
            response_data.update(self._handle_irrigation_inquiry(text))
            
        elif intent == 'fertilizer_advice':
            response_data.update(self._handle_fertilizer_inquiry(text))
            
        elif intent == 'crop_information':
            response_data.update(self._handle_crop_inquiry(text))
            
        else:
            response_data['text_response'] = "I'm not sure I understand. Could you please rephrase your question about farming?"
        
        response_data['voice_response'] = self._generate_voice_response(response_data['text_response'])
        
        return response_data
    
    def _classify_intent(self, text: str) -> str:
        """Classify user intent based on keywords"""
        keywords = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
            'weather_inquiry': ['weather', 'rain', 'temperature', 'forecast', 'climate'],
            'disease_diagnosis': ['disease', 'sick', 'spots', 'dying', 'problem', 'issue'],
            'irrigation_advice': ['water', 'irrigation', 'watering', 'moisture', 'dry'],
            'fertilizer_advice': ['fertilizer', 'nutrient', 'feeding', 'soil', 'growth'],
            'crop_information': ['plant', 'crop', 'grow', 'cultivation', 'farming', 'harvest']
        }
        
        for intent, words in keywords.items():
            if any(word in text for word in words):
                return intent
        
        return 'unknown'
    
    def _handle_weather_inquiry(self, text: str) -> Dict[str, Any]:
        """Handle weather-related inquiries"""
        return {
            'text_response': "Based on current weather conditions, I recommend checking soil moisture levels and adjusting irrigation accordingly. Would you like me to show you the detailed weather forecast?",
            'actions': ['show_weather_dashboard'],
            'data': {'suggestion': 'check_weather_page'}
        }
    
    def _handle_disease_inquiry(self, text: str) -> Dict[str, Any]:
        """Handle disease diagnosis inquiries"""
        # Extract crop type if mentioned
        crop_mentioned = None
        for crop in self.knowledge_base['crops'].keys():
            if crop in text:
                crop_mentioned = crop
                break
        
        response = "I can help diagnose crop diseases. "
        if crop_mentioned:
            diseases = self.knowledge_base['crops'][crop_mentioned]['common_diseases']
            response += f"For {crop_mentioned}, common diseases include {', '.join(diseases)}. "
        
        response += "Please upload an image of your affected crops for detailed analysis."
        
        return {
            'text_response': response,
            'actions': ['open_disease_detection'],
            'data': {'crop_type': crop_mentioned}
        }
    
    def _handle_irrigation_inquiry(self, text: str) -> Dict[str, Any]:
        """Handle irrigation advice inquiries"""
        return {
            'text_response': "For optimal irrigation, consider soil moisture, weather forecast, and crop growth stage. I can create a personalized irrigation schedule for you.",
            'actions': ['show_irrigation_calculator'],
            'data': {'suggestion': 'smart_irrigation'}
        }
    
    def _handle_fertilizer_inquiry(self, text: str) -> Dict[str, Any]:
        """Handle fertilizer advice inquiries"""
        return {
            'text_response': "Fertilizer recommendations depend on soil analysis, crop type, and growth stage. Let me help you create a fertilization plan.",
            'actions': ['show_soil_monitoring'],
            'data': {'suggestion': 'fertilizer_calculator'}
        }
    
    def _handle_crop_inquiry(self, text: str) -> Dict[str, Any]:
        """Handle crop information inquiries"""
        # Extract crop type
        crop_mentioned = None
        for crop in self.knowledge_base['crops'].keys():
            if crop in text:
                crop_mentioned = crop
                break
        
        if crop_mentioned:
            crop_info = self.knowledge_base['crops'][crop_mentioned]
            response = f"For {crop_mentioned}: Planting season is {crop_info['planting_season']}, harvest time is {crop_info['harvest_time']}, water needs are {crop_info['water_needs']}, and optimal temperature is {crop_info['optimal_temp']}."
        else:
            response = "I have information about wheat, corn, rice, and many other crops. Which crop would you like to know about?"
        
        return {
            'text_response': response,
            'actions': ['show_crop_database'],
            'data': {'crop_type': crop_mentioned}
        }
    
    def _generate_voice_response(self, text: str) -> str:
        """Generate voice-friendly response text"""
        # Simplify technical terms for voice synthesis
        voice_text = text.replace('°C', ' degrees Celsius')
        voice_text = voice_text.replace('%', ' percent')
        voice_text = voice_text.replace('&', ' and ')
        
        return voice_text
    
    def get_daily_report(self, farm_data: Dict[str, Any]) -> str:
        """Generate daily voice report"""
        report_parts = [
            f"Good morning! Here's your daily farm report for {datetime.now().strftime('%B %d, %Y')}."
        ]
        
        if 'weather' in farm_data:
            weather = farm_data['weather']
            report_parts.append(f"Today's weather: {weather.get('condition', 'partly cloudy')} with a high of {weather.get('temperature', 25)} degrees and {weather.get('humidity', 65)} percent humidity.")
        
        if 'soil_moisture' in farm_data:
            moisture = farm_data['soil_moisture']
            if moisture < 30:
                report_parts.append("Soil moisture is low. Consider irrigating today.")
            elif moisture > 80:
                report_parts.append("Soil moisture is high. Monitor for potential drainage issues.")
        
        if 'alerts' in farm_data:
            alerts = farm_data['alerts']
            if alerts:
                report_parts.append(f"You have {len(alerts)} alerts requiring attention.")
        
        report_parts.append("Have a productive day in the field!")
        
        return " ".join(report_parts)
    
    def get_crop_recommendations(self, conditions: Dict[str, Any]) -> List[str]:
        """Get intelligent crop recommendations based on conditions"""
        recommendations = []
        
        # Temperature-based recommendations
        temp = conditions.get('temperature', 20)
        if temp < 15:
            recommendations.append("Consider cold-hardy crops like winter wheat or barley")
        elif temp > 30:
            recommendations.append("Hot weather crops like sorghum or millet would thrive")
        else:
            recommendations.append("Moderate temperatures are ideal for corn, soybeans, or wheat")
        
        # Rainfall-based recommendations
        rainfall = conditions.get('rainfall', 500)
        if rainfall < 300:
            recommendations.append("Low rainfall suggests drought-resistant crops")
        elif rainfall > 1000:
            recommendations.append("High rainfall areas are perfect for rice cultivation")
        
        # Soil-based recommendations
        soil_ph = conditions.get('soil_ph', 6.5)
        if soil_ph < 6.0:
            recommendations.append("Acidic soil: consider blueberries or potatoes")
        elif soil_ph > 7.5:
            recommendations.append("Alkaline soil: good for barley or sugar beets")
        
        return recommendations

class ExpertChatbot:
    def __init__(self):
        self.conversation_history = []
        self.context = {}
        
    def chat(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process chat message and return expert response"""
        if context:
            self.context.update(context)
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'context': self.context.copy()
        })
        
        # Generate response based on expertise areas
        response = self._generate_expert_response(user_message)
        
        # Add response to history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'assistant': response['message'],
            'confidence': response['confidence']
        })
        
        return response
    
    def _generate_expert_response(self, message: str) -> Dict[str, Any]:
        """Generate expert agricultural response"""
        message_lower = message.lower()
        
        # Expertise areas and responses
        if any(word in message_lower for word in ['disease', 'pest', 'infection', 'sick']):
            return self._disease_expert_response(message)
        elif any(word in message_lower for word in ['soil', 'fertilizer', 'nutrient', 'ph']):
            return self._soil_expert_response(message)
        elif any(word in message_lower for word in ['weather', 'rain', 'drought', 'climate']):
            return self._weather_expert_response(message)
        elif any(word in message_lower for word in ['yield', 'harvest', 'production']):
            return self._yield_expert_response(message)
        else:
            return self._general_expert_response(message)
    
    def _disease_expert_response(self, message: str) -> Dict[str, Any]:
        return {
            'message': "As a plant pathology expert, I can help diagnose and treat crop diseases. Could you describe the symptoms you're seeing, or better yet, upload a photo? Key things to note: leaf color changes, spots, wilting patterns, and affected plant parts.",
            'confidence': 90,
            'expertise_area': 'Plant Pathology',
            'follow_up_questions': [
                "What crop are you growing?",
                "When did you first notice the symptoms?",
                "Are the symptoms spreading?",
                "What's the weather been like recently?"
            ]
        }
    
    def _soil_expert_response(self, message: str) -> Dict[str, Any]:
        return {
            'message': "As a soil scientist, I recommend starting with a comprehensive soil test. Healthy soil is the foundation of successful farming. Key parameters include pH (6.0-7.0 optimal for most crops), nutrient levels (N-P-K), organic matter content, and soil structure.",
            'confidence': 95,
            'expertise_area': 'Soil Science',
            'follow_up_questions': [
                "When was your last soil test?",
                "What crops are you planning to grow?",
                "Have you noticed any soil compaction issues?",
                "What's your current fertilization program?"
            ]
        }
    
    def _weather_expert_response(self, message: str) -> Dict[str, Any]:
        return {
            'message': "Weather management is crucial for crop success. I recommend monitoring not just current conditions, but 7-14 day forecasts for planning. Key factors: temperature extremes, precipitation timing, humidity for disease pressure, and wind for spray applications.",
            'confidence': 85,
            'expertise_area': 'Agricultural Meteorology',
            'follow_up_questions': [
                "What region are you farming in?",
                "What's your biggest weather concern?",
                "Do you have weather monitoring equipment?",
                "How do you currently get weather information?"
            ]
        }
    
    def _yield_expert_response(self, message: str) -> Dict[str, Any]:
        return {
            'message': "Maximizing yield requires optimizing multiple factors: genetics (seed variety), environment (weather, soil), and management (nutrition, pest control, timing). The key is identifying your limiting factors and addressing them systematically.",
            'confidence': 88,
            'expertise_area': 'Crop Production',
            'follow_up_questions': [
                "What yields are you currently achieving?",
                "What's your target yield?",
                "What varieties are you growing?",
                "What do you think limits your yields?"
            ]
        }
    
    def _general_expert_response(self, message: str) -> Dict[str, Any]:
        return {
            'message': "I'm here to help with all aspects of modern agriculture. Whether it's crop production, soil management, pest control, or farm business decisions, I can provide expert guidance. What specific challenge are you facing?",
            'confidence': 75,
            'expertise_area': 'General Agriculture',
            'follow_up_questions': [
                "What type of farming operation do you have?",
                "What's your main crop or focus?",
                "What's your biggest current challenge?",
                "How can I best help you today?"
            ]
        }

# Global instances
voice_assistant = VoiceAssistant()
expert_chatbot = ExpertChatbot()
