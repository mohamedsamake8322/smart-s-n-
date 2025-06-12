
import json
from typing import Dict, Any

class TranslationManager:
    def __init__(self):
        self.translations = {
            'en': {
                # Navigation and Main Menu
                'title': 'Agricultural Analytics Platform',
                'subtitle': 'AI-Powered Agricultural Intelligence Platform',
                'navigation': 'Navigation',
                'dashboard': 'Dashboard',
                'yield_prediction': 'Yield Prediction',
                'weather_data': 'Weather Data',
                'soil_monitoring': 'Soil Monitoring',
                'data_upload': 'Data Upload',
                'disease_detection': 'Disease Detection',
                'drone_imagery': 'Drone Imagery',
                'climate_forecasting': 'Climate Forecasting',
                'marketplace': 'Agricultural Marketplace',
                'social_network': 'Agricultural Social Network',
                'iot_monitoring': 'IoT Monitoring',
                'voice_assistant': 'Voice Assistant',
                'blockchain_traceability': 'Blockchain Traceability',
                'profitability_analysis': 'Profitability Analysis',
                'scenario_modeling': 'Scenario Modeling',
                
                # Dashboard
                'key_metrics': 'Key Performance Indicators',
                'total_farms': 'Total Farms',
                'average_yield': 'Average Yield (tons/ha)',
                'total_area': 'Total Area (hectares)',
                'crop_varieties': 'Crop Varieties',
                'total_profit': 'Total Profit ($)',
                'weather_status': 'Weather Status',
                'predictions_made': 'Predictions Made',
                
                # AI Predictions
                'ai_prediction': 'AI-Powered Prediction',
                'advanced_regression': 'Advanced Multi-Variable Regression',
                'time_series_analysis': 'Time Series Analysis',
                'crop_information': 'Crop Information',
                'environmental_conditions': 'Environmental Conditions',
                'generate_prediction': 'Generate Prediction',
                'prediction_confidence': 'Prediction Confidence',
                'historical_trends': 'Historical Trends',
                
                # IoT and Automation
                'smart_irrigation': 'Smart Irrigation System',
                'automatic_detection': 'Automatic Plant Stress Detection',
                'real_time_monitoring': 'Real-Time Monitoring',
                'sensor_data': 'Sensor Data',
                'automated_actions': 'Automated Actions',
                'irrigation_schedule': 'Irrigation Schedule',
                
                # Blockchain
                'product_authenticity': 'Product Authenticity',
                'supply_chain': 'Supply Chain Transparency',
                'certification': 'Crop Certification',
                'environmental_premiums': 'Environmental Premiums',
                'traceability_record': 'Traceability Record',
                
                # Voice Assistant
                'voice_reports': 'Voice Reports',
                'audio_alerts': 'Audio Alerts',
                'speech_synthesis': 'Speech Synthesis',
                'expert_chatbot': 'Expert Agricultural Chatbot',
                'instant_recommendations': 'Instant Recommendations',
                
                # Common Actions
                'upload': 'Upload',
                'download': 'Download',
                'export': 'Export',
                'save': 'Save',
                'delete': 'Delete',
                'edit': 'Edit',
                'view': 'View',
                'analyze': 'Analyze',
                'predict': 'Predict',
                'optimize': 'Optimize',
                
                # Status Messages
                'success': 'Success',
                'error': 'Error',
                'warning': 'Warning',
                'info': 'Information',
                'loading': 'Loading...',
                'processing': 'Processing...',
                'completed': 'Completed',
                'failed': 'Failed'
            },
            'fr': {
                # Navigation et Menu Principal
                'title': 'Plateforme d\'Analyse Agricole',
                'subtitle': 'Plateforme d\'Intelligence Agricole IA',
                'navigation': 'Navigation',
                'dashboard': 'Tableau de Bord',
                'yield_prediction': 'Prédiction de Rendement',
                'weather_data': 'Données Météo',
                'soil_monitoring': 'Surveillance du Sol',
                'data_upload': 'Téléchargement de Données',
                'disease_detection': 'Détection de Maladies',
                'drone_imagery': 'Imagerie Drone',
                'climate_forecasting': 'Prévision Climatique',
                'marketplace': 'Marché Agricole',
                'social_network': 'Réseau Social Agricole',
                'iot_monitoring': 'Surveillance IoT',
                'voice_assistant': 'Assistant Vocal',
                'blockchain_traceability': 'Traçabilité Blockchain',
                'profitability_analysis': 'Analyse de Rentabilité',
                'scenario_modeling': 'Modélisation de Scénarios',
                
                # Tableau de Bord
                'key_metrics': 'Indicateurs Clés de Performance',
                'total_farms': 'Total Fermes',
                'average_yield': 'Rendement Moyen (tonnes/ha)',
                'total_area': 'Surface Totale (hectares)',
                'crop_varieties': 'Variétés de Cultures',
                'total_profit': 'Profit Total ($)',
                'weather_status': 'État Météo',
                'predictions_made': 'Prédictions Effectuées',
                
                # Actions Communes
                'upload': 'Télécharger',
                'download': 'Télécharger',
                'export': 'Exporter',
                'save': 'Sauvegarder',
                'delete': 'Supprimer',
                'edit': 'Modifier',
                'view': 'Voir',
                'analyze': 'Analyser',
                'predict': 'Prédire',
                'optimize': 'Optimiser'
            },
            'es': {
                'title': 'Plataforma de Análisis Agrícola',
                'subtitle': 'Plataforma de Inteligencia Agrícola IA',
                'navigation': 'Navegación',
                'dashboard': 'Panel de Control',
                'yield_prediction': 'Predicción de Rendimiento',
                'weather_data': 'Datos Meteorológicos',
                'soil_monitoring': 'Monitoreo del Suelo',
                'data_upload': 'Carga de Datos',
                'disease_detection': 'Detección de Enfermedades',
                'drone_imagery': 'Imágenes de Drones',
                'climate_forecasting': 'Pronóstico Climático',
                'marketplace': 'Mercado Agrícola',
                'social_network': 'Red Social Agrícola',
                'iot_monitoring': 'Monitoreo IoT'
            },
            'de': {
                'title': 'Landwirtschaftliche Analyseplattform',
                'subtitle': 'KI-gestützte Landwirtschaftliche Intelligenzplattform',
                'navigation': 'Navigation',
                'dashboard': 'Dashboard',
                'yield_prediction': 'Ertragsvorhersage',
                'weather_data': 'Wetterdaten',
                'soil_monitoring': 'Bodenüberwachung',
                'data_upload': 'Datenupload',
                'disease_detection': 'Krankheitserkennung'
            },
            'zh': {
                'title': '农业分析平台',
                'subtitle': 'AI驱动的农业智能平台',
                'navigation': '导航',
                'dashboard': '仪表板',
                'yield_prediction': '产量预测',
                'weather_data': '天气数据',
                'soil_monitoring': '土壤监测',
                'data_upload': '数据上传',
                'disease_detection': '病害检测'
            }
        }
    
    def get_text(self, key: str, lang: str = 'en', **kwargs) -> str:
        """Get translated text with optional formatting"""
        try:
            text = self.translations[lang].get(key, self.translations['en'].get(key, key))
            if kwargs:
                return text.format(**kwargs)
            return text
        except:
            return key
    
    def get_available_languages(self) -> Dict[str, str]:
        return {
            'en': '🇺🇸 English',
            'fr': '🇫🇷 Français',
            'es': '🇪🇸 Español',
            'de': '🇩🇪 Deutsch',
            'zh': '🇨🇳 中文'
        }

# Global translation manager instance
translator = TranslationManager()
