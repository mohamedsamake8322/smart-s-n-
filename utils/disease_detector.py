
import numpy as np
import pandas as pd
import cv2
from PIL import Image, ImageEnhance
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2, ResNet50, EfficientNetB0
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
from tensorflow.keras.preprocessing import image
import joblib
import os
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DiseaseDetector:
    """
    Détecteur de maladies agricoles utilisant des CNN pré-entraînés
    Supporte plusieurs architectures et optimisations pour Replit
    """
    
    def __init__(self):
        self.models = {}
        self.preprocessors = {}
        self.class_labels = {}
        self.model_configs = {
            'mobilenetv2': {
                'input_size': (224, 224),
                'preprocess_func': mobilenet_preprocess,
                'base_model': MobileNetV2
            },
            'resnet50': {
                'input_size': (224, 224),
                'preprocess_func': resnet_preprocess,
                'base_model': ResNet50
            },
            'efficientnet': {
                'input_size': (224, 224),
                'preprocess_func': efficientnet_preprocess,
                'base_model': EfficientNetB0
            }
        }
        
        # Initialize default disease classes
        self.disease_classes = [
            'Healthy',
            'Tomato_Late_blight',
            'Tomato_Early_blight',
            'Tomato_Bacterial_spot',
            'Tomato_Septoria_leaf_spot',
            'Potato_Late_blight',
            'Potato_Early_blight',
            'Corn_Common_rust',
            'Corn_Northern_Leaf_Blight',
            'Wheat_Leaf_rust',
            'Wheat_Yellow_rust',
            'Rice_Blast',
            'Rice_Brown_spot',
            'Pepper_Bacterial_spot',
            'Grape_Black_rot',
            'Grape_Powdery_mildew'
        ]
        
        # Create simplified models for demo (in production, load real trained models)
        self._initialize_demo_models()
    
    def _initialize_demo_models(self):
        """
        Initialise les modèles de démonstration
        En production, ces modèles seraient chargés depuis des fichiers pré-entraînés
        """
        try:
            # For demo purposes, we'll use feature extraction + simple classifier
            # In production, you would load your trained CNN models here
            
            for model_name, config in self.model_configs.items():
                print(f"Initialisation du modèle {model_name}...")
                
                # Load base model for feature extraction
                base_model = config['base_model'](
                    weights='imagenet',
                    include_top=False,
                    input_shape=(*config['input_size'], 3),
                    pooling='avg'
                )
                
                # Create a simple classification head
                inputs = tf.keras.Input(shape=(*config['input_size'], 3))
                x = base_model(inputs, training=False)
                x = tf.keras.layers.Dropout(0.2)(x)
                outputs = tf.keras.layers.Dense(len(self.disease_classes), activation='softmax')(x)
                
                model = tf.keras.Model(inputs, outputs)
                
                # Initialize with random weights (in production, load trained weights)
                model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                self.models[model_name] = model
                self.preprocessors[model_name] = config['preprocess_func']
                self.class_labels[model_name] = self.disease_classes
                
                print(f"Modèle {model_name} initialisé avec succès")
                
        except Exception as e:
            print(f"Erreur lors de l'initialisation des modèles: {e}")
            # Fallback to heuristic detection
            self._initialize_heuristic_detector()
    
    def _initialize_heuristic_detector(self):
        """
        Détecteur heuristique de fallback basé sur l'analyse d'image
        """
        print("Initialisation du détecteur heuristique...")
        self.heuristic_mode = True
    
    def preprocess_image(self, image_pil: Image.Image, model_type: str = 'mobilenetv2') -> np.ndarray:
        """
        Préprocessing de l'image pour le modèle spécifié
        
        Args:
            image_pil: Image PIL
            model_type: Type de modèle à utiliser
            
        Returns:
            Image preprocessée sous forme de tensor
        """
        try:
            if model_type not in self.model_configs:
                model_type = 'mobilenetv2'
            
            config = self.model_configs[model_type]
            
            # Resize image
            img_resized = image_pil.resize(config['input_size'])
            
            # Convert to RGB if necessary
            if img_resized.mode != 'RGB':
                img_resized = img_resized.convert('RGB')
            
            # Convert to array
            img_array = np.array(img_resized)
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            # Apply model-specific preprocessing
            if model_type in self.preprocessors:
                img_array = self.preprocessors[model_type](img_array)
            else:
                # Default preprocessing
                img_array = img_array.astype(np.float32) / 255.0
            
            return img_array
            
        except Exception as e:
            print(f"Erreur lors du preprocessing: {e}")
            # Return default processed image
            return np.zeros((1, 224, 224, 3))
    
    def predict_disease(self, image_pil: Image.Image, model_type: str = 'mobilenetv2',
                       confidence_threshold: float = 0.7, crop_filter: List[str] = None) -> List[Dict]:
        """
        Prédiction de maladie sur une image
        
        Args:
            image_pil: Image PIL à analyser
            model_type: Type de modèle à utiliser
            confidence_threshold: Seuil de confiance minimum
            crop_filter: Liste des cultures à considérer
            
        Returns:
            Liste des prédictions ordonnées par confiance
        """
        try:
            if hasattr(self, 'heuristic_mode') and self.heuristic_mode:
                return self._heuristic_disease_detection(image_pil, crop_filter)
            
            # Preprocess image
            processed_img = self.preprocess_image(image_pil, model_type)
            
            # Get model
            if model_type not in self.models:
                model_type = list(self.models.keys())[0]  # Use first available model
            
            model = self.models[model_type]
            class_labels = self.class_labels[model_type]
            
            # Make prediction
            predictions = model.predict(processed_img, verbose=0)
            predictions = predictions[0]  # Remove batch dimension
            
            # Sort predictions by confidence
            sorted_indices = np.argsort(predictions)[::-1]
            
            results = []
            for idx in sorted_indices:
                confidence = float(predictions[idx]) * 100
                disease_name = class_labels[idx]
                
                # Apply crop filter if specified
                if crop_filter and not self._disease_matches_crops(disease_name, crop_filter):
                    continue
                
                # Apply confidence threshold
                if confidence < confidence_threshold * 100:
                    break
                
                # Get disease severity and urgency
                severity, urgency = self._assess_disease_severity(disease_name, confidence)
                
                results.append({
                    'disease': disease_name,
                    'confidence': confidence,
                    'severity': severity,
                    'urgency': urgency,
                    'model_used': model_type
                })
            
            # If no predictions meet threshold, return top prediction anyway
            if not results and len(sorted_indices) > 0:
                top_idx = sorted_indices[0]
                confidence = float(predictions[top_idx]) * 100
                disease_name = class_labels[top_idx]
                severity, urgency = self._assess_disease_severity(disease_name, confidence)
                
                results.append({
                    'disease': disease_name,
                    'confidence': confidence,
                    'severity': severity,
                    'urgency': urgency,
                    'model_used': model_type
                })
            
            return results
            
        except Exception as e:
            print(f"Erreur lors de la prédiction: {e}")
            return self._heuristic_disease_detection(image_pil, crop_filter)
    
    def _heuristic_disease_detection(self, image_pil: Image.Image, crop_filter: List[str] = None) -> List[Dict]:
        """
        Détection heuristique basée sur l'analyse des caractéristiques de l'image
        """
        try:
            # Convert to OpenCV format
            img_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            
            # Analyze image characteristics
            analysis = self._analyze_image_features(img_cv)
            
            # Heuristic disease detection based on visual features
            results = []
            
            # Check for brown/yellow spots (potential blight)
            if analysis['brown_spots'] > 0.1:
                results.append({
                    'disease': 'Tomato_Late_blight',
                    'confidence': min(95, analysis['brown_spots'] * 100 + 60),
                    'severity': 'Élevée' if analysis['brown_spots'] > 0.3 else 'Modérée',
                    'urgency': 'Haute' if analysis['brown_spots'] > 0.3 else 'Moyenne',
                    'model_used': 'heuristic'
                })
            
            # Check for powdery appearance (potential mildew)
            if analysis['white_patches'] > 0.15:
                results.append({
                    'disease': 'Grape_Powdery_mildew',
                    'confidence': min(90, analysis['white_patches'] * 100 + 50),
                    'severity': 'Modérée',
                    'urgency': 'Moyenne',
                    'model_used': 'heuristic'
                })
            
            # Check for rust-colored spots
            if analysis['rust_spots'] > 0.1:
                results.append({
                    'disease': 'Corn_Common_rust',
                    'confidence': min(88, analysis['rust_spots'] * 100 + 55),
                    'severity': 'Modérée',
                    'urgency': 'Moyenne',
                    'model_used': 'heuristic'
                })
            
            # If no specific diseases detected, assume healthy
            if not results:
                results.append({
                    'disease': 'Healthy',
                    'confidence': 75.0,
                    'severity': 'Aucune',
                    'urgency': 'Aucune',
                    'model_used': 'heuristic'
                })
            
            # Add healthy as alternative if diseases were detected
            elif results[0]['disease'] != 'Healthy':
                results.append({
                    'disease': 'Healthy',
                    'confidence': max(10, 80 - results[0]['confidence']),
                    'severity': 'Aucune',
                    'urgency': 'Aucune',
                    'model_used': 'heuristic'
                })
            
            # Sort by confidence
            results.sort(key=lambda x: x['confidence'], reverse=True)
            
            return results
            
        except Exception as e:
            print(f"Erreur dans la détection heuristique: {e}")
            return [{
                'disease': 'Healthy',
                'confidence': 50.0,
                'severity': 'Inconnue',
                'urgency': 'Inconnue',
                'model_used': 'fallback'
            }]
    
    def _analyze_image_features(self, img_cv: np.ndarray) -> Dict[str, float]:
        """
        Analyse les caractéristiques visuelles de l'image
        """
        try:
            # Convert to HSV for better color analysis
            img_hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for different symptoms
            # Brown spots (blight symptoms)
            brown_lower = np.array([10, 50, 20])
            brown_upper = np.array([20, 255, 200])
            brown_mask = cv2.inRange(img_hsv, brown_lower, brown_upper)
            brown_ratio = np.sum(brown_mask > 0) / (img_cv.shape[0] * img_cv.shape[1])
            
            # White patches (powdery mildew)
            white_lower = np.array([0, 0, 200])
            white_upper = np.array([180, 30, 255])
            white_mask = cv2.inRange(img_hsv, white_lower, white_upper)
            white_ratio = np.sum(white_mask > 0) / (img_cv.shape[0] * img_cv.shape[1])
            
            # Rust colored spots
            rust_lower = np.array([5, 100, 100])
            rust_upper = np.array([15, 255, 255])
            rust_mask = cv2.inRange(img_hsv, rust_lower, rust_upper)
            rust_ratio = np.sum(rust_mask > 0) / (img_cv.shape[0] * img_cv.shape[1])
            
            # Yellow spots (various diseases)
            yellow_lower = np.array([20, 50, 50])
            yellow_upper = np.array([30, 255, 255])
            yellow_mask = cv2.inRange(img_hsv, yellow_lower, yellow_upper)
            yellow_ratio = np.sum(yellow_mask > 0) / (img_cv.shape[0] * img_cv.shape[1])
            
            # Texture analysis using standard deviation
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            texture_variance = np.var(gray)
            
            return {
                'brown_spots': brown_ratio,
                'white_patches': white_ratio,
                'rust_spots': rust_ratio,
                'yellow_spots': yellow_ratio,
                'texture_variance': texture_variance / 10000,  # Normalize
                'overall_health': 1.0 - min(1.0, brown_ratio + white_ratio + rust_ratio + yellow_ratio)
            }
            
        except Exception as e:
            print(f"Erreur dans l'analyse des caractéristiques: {e}")
            return {
                'brown_spots': 0.0,
                'white_patches': 0.0,
                'rust_spots': 0.0,
                'yellow_spots': 0.0,
                'texture_variance': 0.0,
                'overall_health': 0.5
            }
    
    def _disease_matches_crops(self, disease_name: str, crop_filter: List[str]) -> bool:
        """
        Vérifie si une maladie correspond aux cultures filtrées
        """
        if not crop_filter:
            return True
        
        # Map diseases to crops
        disease_crop_mapping = {
            'Tomato': ['tomato'],
            'Potato': ['potato', 'pomme de terre'],
            'Corn': ['corn', 'maïs'],
            'Wheat': ['wheat', 'blé'],
            'Rice': ['rice', 'riz'],
            'Pepper': ['pepper', 'poivron'],
            'Grape': ['grape', 'raisin']
        }
        
        for crop_prefix, crop_names in disease_crop_mapping.items():
            if disease_name.startswith(crop_prefix):
                for filter_crop in crop_filter:
                    if filter_crop.lower() in [c.lower() for c in crop_names]:
                        return True
        
        # If disease doesn't match any specific crop, allow it
        return True
    
    def _assess_disease_severity(self, disease_name: str, confidence: float) -> Tuple[str, str]:
        """
        Évalue la sévérité et l'urgence d'une maladie
        """
        # High severity diseases
        high_severity_diseases = [
            'Late_blight', 'Black_rot', 'Blast'
        ]
        
        # Moderate severity diseases
        moderate_severity_diseases = [
            'Early_blight', 'Bacterial_spot', 'Leaf_rust', 'Common_rust'
        ]
        
        if disease_name == 'Healthy':
            return 'Aucune', 'Aucune'
        
        # Determine severity based on disease type
        severity = 'Faible'
        urgency = 'Faible'
        
        for high_disease in high_severity_diseases:
            if high_disease in disease_name:
                severity = 'Élevée'
                urgency = 'Haute'
                break
        
        if severity == 'Faible':
            for mod_disease in moderate_severity_diseases:
                if mod_disease in disease_name:
                    severity = 'Modérée'
                    urgency = 'Moyenne'
                    break
        
        # Adjust based on confidence
        if confidence > 90:
            if urgency == 'Moyenne':
                urgency = 'Haute'
            elif urgency == 'Faible':
                urgency = 'Moyenne'
        
        return severity, urgency
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur les modèles disponibles
        """
        model_info = {}
        
        for model_name in self.models.keys():
            config = self.model_configs.get(model_name, {})
            model_info[model_name] = {
                'input_size': config.get('input_size', (224, 224)),
                'num_classes': len(self.class_labels.get(model_name, [])),
                'status': 'loaded'
            }
        
        return model_info
    
    def benchmark_models(self, test_images: List[Image.Image]) -> Dict[str, Dict]:
        """
        Benchmark des différents modèles sur un ensemble d'images test
        """
        results = {}
        
        for model_name in self.models.keys():
            print(f"Benchmarking {model_name}...")
            
            start_time = datetime.now()
            predictions = []
            
            for img in test_images:
                pred = self.predict_disease(img, model_type=model_name)
                predictions.append(pred[0] if pred else None)
            
            end_time = datetime.now()
            
            # Calculate metrics
            processing_time = (end_time - start_time).total_seconds()
            avg_time_per_image = processing_time / len(test_images)
            
            valid_predictions = [p for p in predictions if p is not None]
            avg_confidence = np.mean([p['confidence'] for p in valid_predictions]) if valid_predictions else 0
            
            results[model_name] = {
                'total_time': processing_time,
                'avg_time_per_image': avg_time_per_image,
                'avg_confidence': avg_confidence,
                'success_rate': len(valid_predictions) / len(test_images) * 100
            }
        
        return results


def preprocess_image(image_pil: Image.Image, target_size: Tuple[int, int] = (224, 224)) -> Image.Image:
    """
    Fonction utilitaire pour le preprocessing d'image
    """
    # Resize maintaining aspect ratio
    image_pil.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    # Create new image with target size and paste resized image
    new_image = Image.new('RGB', target_size, (255, 255, 255))
    
    # Calculate position to center the image
    x = (target_size[0] - image_pil.width) // 2
    y = (target_size[1] - image_pil.height) // 2
    
    new_image.paste(image_pil, (x, y))
    
    return new_image


def enhance_image_quality(image_pil: Image.Image) -> Image.Image:
    """
    Améliore la qualité de l'image pour une meilleure détection
    """
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image_pil)
    image_pil = enhancer.enhance(1.2)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image_pil)
    image_pil = enhancer.enhance(1.1)
    
    # Enhance color
    enhancer = ImageEnhance.Color(image_pil)
    image_pil = enhancer.enhance(1.1)
    
    return image_pil
