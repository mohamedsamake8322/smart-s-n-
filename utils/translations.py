﻿
import json
from typing import Dict, Any
translations = {}
translations.update({
    'smart_fertilization': {
        'en': 'Smart Fertilization',
        'fr': 'Fertilisation Intelligente'
    }
})

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
                'yield_prediction': 'PrÃ©diction de Rendement',
                'weather_data': 'DonnÃ©es MÃ©tÃ©o',
                'soil_monitoring': 'Surveillance du Sol',
                'data_upload': 'TÃ©lÃ©chargement de DonnÃ©es',
                'disease_detection': 'DÃ©tection de Maladies',
                'drone_imagery': 'Imagerie Drone',
                'climate_forecasting': 'PrÃ©vision Climatique',
                'marketplace': 'MarchÃ© Agricole',
                'social_network': 'RÃ©seau Social Agricole',
                'iot_monitoring': 'Surveillance IoT',
                'voice_assistant': 'Assistant Vocal',
                'blockchain_traceability': 'TraÃ§abilitÃ© Blockchain',
                'profitability_analysis': 'Analyse de RentabilitÃ©',
                'scenario_modeling': 'ModÃ©lisation de ScÃ©narios',
                
                # Tableau de Bord
                'key_metrics': 'Indicateurs ClÃ©s de Performance',
                'total_farms': 'Total Fermes',
                'average_yield': 'Rendement Moyen (tonnes/ha)',
                'total_area': 'Surface Totale (hectares)',
                'crop_varieties': 'VariÃ©tÃ©s de Cultures',
                'total_profit': 'Profit Total ($)',
                'weather_status': 'Ã‰tat MÃ©tÃ©o',
                'predictions_made': 'PrÃ©dictions EffectuÃ©es',
                
                # Actions Communes
                'upload': 'TÃ©lÃ©charger',
                'download': 'TÃ©lÃ©charger',
                'export': 'Exporter',
                'save': 'Sauvegarder',
                'delete': 'Supprimer',
                'edit': 'Modifier',
                'view': 'Voir',
                'analyze': 'Analyser',
                'predict': 'PrÃ©dire',
                'optimize': 'Optimiser'
            },
            'es': {
                'title': 'Plataforma de AnÃ¡lisis AgrÃ­cola',
                'subtitle': 'Plataforma de Inteligencia AgrÃ­cola IA',
                'navigation': 'NavegaciÃ³n',
                'dashboard': 'Panel de Control',
                'yield_prediction': 'PredicciÃ³n de Rendimiento',
                'weather_data': 'Datos MeteorolÃ³gicos',
                'soil_monitoring': 'Monitoreo del Suelo',
                'data_upload': 'Carga de Datos',
                'disease_detection': 'DetecciÃ³n de Enfermedades',
                'drone_imagery': 'ImÃ¡genes de Drones',
                'climate_forecasting': 'PronÃ³stico ClimÃ¡tico',
                'marketplace': 'Mercado AgrÃ­cola',
                'social_network': 'Red Social AgrÃ­cola',
                'iot_monitoring': 'Monitoreo IoT'
            },
            'de': {
                'title': 'Landwirtschaftliche Analyseplattform',
                'subtitle': 'KI-gestÃ¼tzte Landwirtschaftliche Intelligenzplattform',
                'navigation': 'Navigation',
                'dashboard': 'Dashboard',
                'yield_prediction': 'Ertragsvorhersage',
                'weather_data': 'Wetterdaten',
                'soil_monitoring': 'BodenÃ¼berwachung',
                'data_upload': 'Datenupload',
                'disease_detection': 'Krankheitserkennung'
            },
            'zh': {
                'title': 'å†œä¸šåˆ†æžå¹³å°',
                'subtitle': 'AIé©±åŠ¨çš„å†œä¸šæ™ºèƒ½å¹³å°',
                'navigation': 'å¯¼èˆª',
                'dashboard': 'ä»ªè¡¨æ¿',
                'yield_prediction': 'äº§é‡é¢„æµ‹',
                'weather_data': 'å¤©æ°”æ•°æ®',
                'soil_monitoring': 'åœŸå£¤ç›‘æµ‹',
                'data_upload': 'æ•°æ®ä¸Šä¼ ',
                'disease_detection': 'ç—…å®³æ£€æµ‹'
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
            'en': 'ðŸ‡ºðŸ‡¸ English',
            'fr': 'ðŸ‡«ðŸ‡· FranÃ§ais',
            'es': 'ðŸ‡ªðŸ‡¸ EspaÃ±ol',
            'de': 'ðŸ‡©ðŸ‡ª Deutsch',
            'zh': 'ðŸ‡¨ðŸ‡³ ä¸­æ–‡'
        }

# Global translation manager instance
translator = TranslationManager()
# Smart fertilization translations
translations.update({
    'smart_fertilization': {
        'en': 'Smart Fertilization',
        'fr': 'Fertilisation Intelligente'
    },
    'ai_fertilization_subtitle': {
        'en': 'AI-powered fertilization planning and optimization',
        'fr': 'Planification et optimisation de fertilisation par IA'
    },
    'create_plan': {
        'en': 'Create Plan',
        'fr': 'CrÃ©er Plan'
    },
    'crop_database': {
        'en': 'Crop Database',
        'fr': 'Base Cultures'
    },
    'ai_optimization': {
        'en': 'AI Optimization',
        'fr': 'Optimisation IA'
    },
    'cost_analysis': {
        'en': 'Cost Analysis',
        'fr': 'Analyse CoÃ»ts'
    },
    'iot_integration': {
        'en': 'IoT Integration',
        'fr': 'IntÃ©gration IoT'
    },
    'plan_history': {
        'en': 'Plan History',
        'fr': 'Historique Plans'
    },
    'create_fertilization_plan': {
        'en': 'Create Fertilization Plan',
        'fr': 'CrÃ©er Plan de Fertilisation'
    },
    'farm_information': {
        'en': 'Farm Information',
        'fr': 'Informations Exploitation'
    },
    'farmer_name': {
        'en': 'Farmer Name',
        'fr': 'Nom Agriculteur'
    },
    'farmer_name_help': {
        'en': 'Enter the farmer\'s full name',
        'fr': 'Saisir le nom complet de l\'agriculteur'
    },
    'farm_name': {
        'en': 'Farm Name',
        'fr': 'Nom Exploitation'
    },
    'farm_name_help': {
        'en': 'Enter the farm or company name',
        'fr': 'Saisir le nom de l\'exploitation ou sociÃ©tÃ©'
    },
    'crop_type': {
        'en': 'Crop Type',
        'fr': 'Type de Culture'
    },
    'area_hectares': {
        'en': 'Area (hectares)',
        'fr': 'Superficie (hectares)'
    },
    'planting_date': {
        'en': 'Planting Date',
        'fr': 'Date de Semis'
    },
    'target_yield': {
        'en': 'Target Yield (t/ha)',
        'fr': 'Rendement Cible (t/ha)'
    },
    'target_yield_help': {
        'en': 'Expected yield in tons per hectare',
        'fr': 'Rendement attendu en tonnes par hectare'
    },
    'soil_conditions': {
        'en': 'Soil Conditions',
        'fr': 'Conditions du Sol'
    },
    'soil_ph': {
        'en': 'Soil pH',
        'fr': 'pH du Sol'
    },
    'nitrogen_ppm': {
        'en': 'Nitrogen (ppm)',
        'fr': 'Azote (ppm)'
    },
    'phosphorus_ppm': {
        'en': 'Phosphorus (ppm)',
        'fr': 'Phosphore (ppm)'
    },
    'potassium_ppm': {
        'en': 'Potassium (ppm)',
        'fr': 'Potassium (ppm)'
    },
    'organic_matter': {
        'en': 'Organic Matter (%)',
        'fr': 'MatiÃ¨re Organique (%)'
    },
    'soil_moisture': {
        'en': 'Soil Moisture (%)',
        'fr': 'HumiditÃ© Sol (%)'
    },
    'moisture_help': {
        'en': 'Current soil moisture percentage',
        'fr': 'Pourcentage d\'humiditÃ© actuel du sol'
    },
    'generate_plan': {
        'en': 'Generate Plan',
        'fr': 'GÃ©nÃ©rer Plan'
    },
    'generating_plan': {
        'en': 'Generating fertilization plan...',
        'fr': 'GÃ©nÃ©ration du plan de fertilisation...'
    },
    'plan_generated': {
        'en': 'Fertilization plan generated successfully!',
        'fr': 'Plan de fertilisation gÃ©nÃ©rÃ© avec succÃ¨s !'
    },
    'plan_preview': {
        'en': 'Plan Preview',
        'fr': 'AperÃ§u du Plan'
    },
    'generate_pdf': {
        'en': 'Generate PDF',
        'fr': 'GÃ©nÃ©rer PDF'
    },
    'download_pdf': {
        'en': 'Download PDF',
        'fr': 'TÃ©lÃ©charger PDF'
    },
    'create_plan_first': {
        'en': 'Create a fertilization plan first to see the preview',
        'fr': 'CrÃ©ez d\'abord un plan de fertilisation pour voir l\'aperÃ§u'
    },
    'select_crop_info': {
        'en': 'Select crop to view information',
        'fr': 'SÃ©lectionner une culture pour voir les informations'
    },
    'quick_actions': {
        'en': 'Quick Actions',
        'fr': 'Actions Rapides'
    },
    'refresh_data': {
        'en': 'Refresh Data',
        'fr': 'Actualiser DonnÃ©es'
    }
})

