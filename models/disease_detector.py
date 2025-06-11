"""
Advanced Plant Disease Detection System
"""
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import numpy as np
import logging
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image
import json
from datetime import datetime

try:
    import tensorflow as tf
    import cv2
except ImportError as e:
    logging.warning(f"Some libraries not available for disease detection: {e}")

logger = logging.getLogger(__name__)
logging.basicConfig(filename="execution.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("✅ Script exécuté avec succès !")
class DiseaseDetector:
    """Advanced plant disease detection with confidence scoring and treatment recommendations"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.class_names = []
        self.confidence_threshold = 0.7
        self.image_size = (224, 224)
        
        # Disease information database
        self.disease_info = self._load_disease_database()
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """Load the disease detection model"""
        try:
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"Disease detection model loaded from {model_path}")
            
            # Load class names if metadata file exists
            metadata_path = model_path.replace('.h5', '_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.class_names = metadata.get('class_names', [])
                    self.confidence_threshold = metadata.get('confidence_threshold', 0.7)
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading disease detection model: {e}")
            return False
    
    def preprocess_image(self, image_input) -> Optional[np.ndarray]:
        """Preprocess image for model prediction"""
        try:
            # Handle different input types
            if isinstance(image_input, str):  # File path
                image = Image.open(image_input)
            elif isinstance(image_input, Image.Image):  # PIL Image
                image = image_input
            elif isinstance(image_input, np.ndarray):  # NumPy array
                if len(image_input.shape) == 3:
                    image = Image.fromarray(image_input.astype('uint8'))
                else:
                    return None
            else:
                return None
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image
            image = image.resize(self.image_size)
            
            # Convert to numpy array and normalize
            image_array = np.array(image) / 255.0
            
            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
    
    def detect_disease(self, image_input, return_top_k: int = 3) -> Dict[str, Any]:
        """Detect plant disease from image"""
        try:
            if self.model is None:
                return {
                    'error': 'Disease detection model not loaded',
                    'success': False
                }
            
            # Preprocess image
            processed_image = self.preprocess_image(image_input)
            if processed_image is None:
                return {
                    'error': 'Failed to preprocess image',
                    'success': False
                }
            
            # Make prediction
            predictions = self.model.predict(processed_image, verbose=0)
            prediction_scores = predictions[0]
            
            # Get top predictions
            top_indices = np.argsort(prediction_scores)[::-1][:return_top_k]
            
            results = []
            for i, idx in enumerate(top_indices):
                confidence = float(prediction_scores[idx])
                disease_name = self.class_names[idx] if idx < len(self.class_names) else f"Unknown_Class_{idx}"
                
                # Get disease information
                disease_data = self.disease_info.get(disease_name, {})
                
                result = {
                    'rank': i + 1,
                    'disease': disease_name,
                    'confidence': confidence,
                    'severity': self._assess_severity(confidence),
                    'description': disease_data.get('description', 'No description available'),
                    'symptoms': disease_data.get('symptoms', []),
                    'causes': disease_data.get('causes', []),
                    'treatment': disease_data.get('treatment', []),
                    'prevention': disease_data.get('prevention', [])
                }
                results.append(result)
            
            # Determine primary diagnosis
            primary_result = results[0] if results else None
            is_healthy = primary_result and primary_result['disease'].lower() in ['healthy', 'normal', 'no_disease']
            
            return {
                'success': True,
                'primary_diagnosis': primary_result,
                'all_predictions': results,
                'is_healthy': is_healthy,
                'confidence_threshold': self.confidence_threshold,
                'requires_attention': primary_result['confidence'] > self.confidence_threshold if primary_result else False,
                'analysis_timestamp': datetime.now().isoformat(),
                'recommendations': self._generate_recommendations(primary_result) if primary_result else []
            }
            
        except Exception as e:
            logger.error(f"Error in disease detection: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def batch_detect(self, image_list: List) -> List[Dict[str, Any]]:
        """Detect diseases in multiple images"""
        results = []
        
        for i, image in enumerate(image_list):
            try:
                result = self.detect_disease(image)
                result['image_index'] = i
                results.append(result)
            except Exception as e:
                results.append({
                    'image_index': i,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def _assess_severity(self, confidence: float) -> str:
        """Assess disease severity based on confidence score"""
        if confidence < 0.3:
            return "Low"
        elif confidence < 0.6:
            return "Moderate"
        elif confidence < 0.8:
            return "High"
        else:
            return "Severe"
    
    def _generate_recommendations(self, diagnosis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on diagnosis"""
        recommendations = []
        
        if not diagnosis or diagnosis.get('confidence', 0) < self.confidence_threshold:
            recommendations.append("Confidence is low. Consider taking additional photos for better analysis.")
            return recommendations
        
        disease = diagnosis.get('disease', '').lower()
        severity = diagnosis.get('severity', '').lower()
        
        # General recommendations
        if severity in ['high', 'severe']:
            recommendations.append("🚨 Immediate attention required - contact agricultural extension officer")
            recommendations.append("🔬 Consider laboratory testing for accurate identification")
        
        # Specific treatment recommendations
        if diagnosis.get('treatment'):
            recommendations.append("📋 Treatment Options:")
            recommendations.extend([f"  • {treatment}" for treatment in diagnosis['treatment'][:3]])
        
        # Prevention recommendations
        if diagnosis.get('prevention'):
            recommendations.append("🛡️ Prevention Measures:")
            recommendations.extend([f"  • {prevention}" for prevention in diagnosis['prevention'][:3]])
        
        # Additional monitoring
        recommendations.append("📊 Monitor plant health regularly")
        recommendations.append("📸 Take follow-up photos after treatment")
        
        return recommendations
    
    def _load_disease_database(self) -> Dict[str, Dict[str, Any]]:
        """Load comprehensive disease information database"""
        return {
            "Tomato_Bacterial_spot": {
                "description": "Bacterial disease causing dark spots on leaves and fruits",
                "symptoms": [
                    "Small dark spots on leaves",
                    "Yellow halos around spots",
                    "Fruit lesions",
                    "Defoliation in severe cases"
                ],
                "causes": [
                    "Xanthomonas bacteria",
                    "High humidity conditions",
                    "Water splash dispersal",
                    "Warm temperatures (75-86°F)"
                ],
                "treatment": [
                    "Apply copper-based bactericides",
                    "Remove infected plant parts",
                    "Improve air circulation",
                    "Avoid overhead watering"
                ],
                "prevention": [
                    "Use resistant varieties",
                    "Crop rotation",
                    "Drip irrigation",
                    "Field sanitation"
                ]
            },
            "Tomato_Early_blight": {
                "description": "Fungal disease causing brown spots with concentric rings",
                "symptoms": [
                    "Brown spots with target-like rings",
                    "Lower leaves affected first",
                    "Yellowing and wilting",
                    "Stem lesions"
                ],
                "causes": [
                    "Alternaria solani fungus",
                    "High humidity",
                    "Leaf wetness",
                    "Stress conditions"
                ],
                "treatment": [
                    "Apply fungicides (chlorothalonil, mancozeb)",
                    "Remove affected leaves",
                    "Improve plant spacing",
                    "Mulching to prevent soil splash"
                ],
                "prevention": [
                    "Resistant varieties",
                    "Proper plant spacing",
                    "Avoid wetting foliage",
                    "Crop rotation"
                ]
            },
            "Tomato_Late_blight": {
                "description": "Severe fungal disease that can destroy entire crops",
                "symptoms": [
                    "Water-soaked lesions",
                    "White fuzzy growth on leaf undersides",
                    "Brown to black lesions",
                    "Rapid plant collapse"
                ],
                "causes": [
                    "Phytophthora infestans",
                    "Cool, wet conditions",
                    "High humidity",
                    "Poor air circulation"
                ],
                "treatment": [
                    "Apply protective fungicides immediately",
                    "Remove infected plants",
                    "Improve drainage",
                    "Reduce humidity"
                ],
                "prevention": [
                    "Use certified disease-free seeds",
                    "Avoid overhead irrigation",
                    "Provide good air circulation",
                    "Apply preventive fungicides"
                ]
            },
            "Healthy": {
                "description": "Plant appears healthy with no visible disease symptoms",
                "symptoms": [
                    "Green, vigorous foliage",
                    "No spots or lesions",
                    "Normal growth pattern",
                    "Good color"
                ],
                "causes": [
                    "Proper care and nutrition",
                    "Good growing conditions",
                    "Disease prevention practices"
                ],
                "treatment": [
                    "Continue current care routine",
                    "Monitor regularly for changes",
                    "Maintain optimal growing conditions"
                ],
                "prevention": [
                    "Regular monitoring",
                    "Proper nutrition",
                    "Good cultural practices",
                    "Preventive treatments as needed"
                ]
            }
        }
    
    def get_disease_info(self, disease_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific disease"""
        return self.disease_info.get(disease_name, {
            'description': 'Disease information not available',
            'symptoms': [],
            'causes': [],
            'treatment': [],
            'prevention': []
        })
    
    def update_disease_database(self, disease_name: str, disease_data: Dict[str, Any]):
        """Update disease information database"""
        self.disease_info[disease_name] = disease_data
        logger.info(f"Updated disease database for {disease_name}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if self.model is None:
            return {'error': 'No model loaded'}
        
        return {
            'model_loaded': True,
            'input_shape': self.model.input_shape if hasattr(self.model, 'input_shape') else None,
            'output_shape': self.model.output_shape if hasattr(self.model, 'output_shape') else None,
            'num_classes': len(self.class_names),
            'class_names': self.class_names,
            'confidence_threshold': self.confidence_threshold
        }

# Global disease detector instance
disease_detector = DiseaseDetector()

# Convenience functions for backward compatibility
def detect_disease(image_input, return_top_k: int = 3) -> Dict[str, Any]:
    """Detect disease (backward compatibility)"""
    return disease_detector.detect_disease(image_input, return_top_k)

def load_disease_model(model_path: str) -> bool:
    """Load disease model (backward compatibility)"""
    return disease_detector.load_model(model_path)
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ton code principal ici
def main():
    print("✅ Script exécuté avec succès !")
    logging.info("Le script a été exécuté sans erreur.")

if __name__ == "__main__":
    main()
