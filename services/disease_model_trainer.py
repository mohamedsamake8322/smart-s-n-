
import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any
import cv2
from PIL import Image
import joblib

class DiseaseModelTrainer:
    """
    Service d'entraînement des modèles CNN pour la détection de maladies
    Optimisé pour fonctionner sur Replit avec des ressources limitées
    """
    
    def __init__(self):
        self.model = None
        self.training_history = None
        self.class_names = []
        self.model_config = {
            'input_shape': (224, 224, 3),
            'num_classes': 10,
            'batch_size': 16,
            'epochs': 20,
            'learning_rate': 0.001
        }
        
        # Configure TensorFlow for limited resources
        self._configure_tensorflow()
    
    def _configure_tensorflow(self):
        """Configure TensorFlow for optimal performance on Replit"""
        try:
            # Limit GPU memory growth if GPU available
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
            
            # Enable mixed precision for better performance
            tf.keras.mixed_precision.set_global_policy('mixed_float16')
            
        except Exception as e:
            print(f"Configuration TensorFlow: {e}")
    
    def create_efficient_model(self, num_classes: int = 10) -> tf.keras.Model:
        """
        Crée un modèle CNN efficace pour la détection de maladies
        Optimisé pour les ressources limitées de Replit
        """
        
        # Use MobileNetV2 as base for efficiency
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=self.model_config['input_shape'],
            include_top=False,
            weights='imagenet',
            pooling='avg'
        )
        
        # Freeze base model layers for faster training
        base_model.trainable = False
        
        # Add custom classification head
        inputs = tf.keras.Input(shape=self.model_config['input_shape'])
        
        # Data augmentation layer
        x = tf.keras.layers.RandomFlip("horizontal")(inputs)
        x = tf.keras.layers.RandomRotation(0.1)(x)
        x = tf.keras.layers.RandomZoom(0.1)(x)
        
        # Preprocessing
        x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
        
        # Base model
        x = base_model(x, training=False)
        
        # Classification layers
        x = tf.keras.layers.Dropout(0.2)(x)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        outputs = tf.keras.layers.Dense(num_classes, activation='softmax', dtype='float32')(x)
        
        model = tf.keras.Model(inputs, outputs)
        
        # Compile model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.model_config['learning_rate']),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_k_categorical_accuracy']
        )
        
        return model
    
    def prepare_dataset_from_synthetic(self, num_samples_per_class: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Crée un dataset synthétique pour l'entraînement rapide
        """
        print("Création d'un dataset synthétique...")
        
        # Disease classes
        disease_classes = [
            'Healthy', 'Late_blight', 'Early_blight', 'Bacterial_spot',
            'Common_rust', 'Leaf_rust', 'Rice_blast', 'Powdery_mildew',
            'Brown_spot', 'Septoria_leaf_spot'
        ]
        
        self.class_names = disease_classes
        num_classes = len(disease_classes)
        
        # Generate synthetic images
        X = []
        y = []
        
        for class_idx, disease_class in enumerate(disease_classes):
            print(f"Génération de {num_samples_per_class} échantillons pour {disease_class}")
            
            for _ in range(num_samples_per_class):
                # Create synthetic image based on disease characteristics
                img = self._create_synthetic_disease_image(disease_class)
                X.append(img)
                y.append(class_idx)
        
        X = np.array(X, dtype=np.float32) / 255.0
        y = tf.keras.utils.to_categorical(y, num_classes)
        
        print(f"Dataset créé: {X.shape[0]} échantillons, {num_classes} classes")
        return X, y
    
    def _create_synthetic_disease_image(self, disease_class: str) -> np.ndarray:
        """
        Crée une image synthétique pour une classe de maladie
        """
        img_size = 224
        
        # Base healthy leaf (green background)
        img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 50
        img[:, :, 1] = 120  # More green
        
        if disease_class == 'Healthy':
            # Healthy leaf - uniform green with slight variations
            img[:, :, 1] = np.random.randint(100, 140, (img_size, img_size))
            
        elif 'blight' in disease_class.lower():
            # Add brown/dark spots for blight
            num_spots = np.random.randint(3, 8)
            for _ in range(num_spots):
                center_x = np.random.randint(50, img_size - 50)
                center_y = np.random.randint(50, img_size - 50)
                radius = np.random.randint(10, 30)
                
                y, x = np.ogrid[:img_size, :img_size]
                mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
                
                img[mask] = [80, 60, 40]  # Brown color
        
        elif 'rust' in disease_class.lower():
            # Add orange/rust colored pustules
            num_pustules = np.random.randint(20, 50)
            for _ in range(num_pustules):
                x = np.random.randint(0, img_size)
                y = np.random.randint(0, img_size)
                size = np.random.randint(2, 6)
                
                x_start = max(0, x - size)
                x_end = min(img_size, x + size)
                y_start = max(0, y - size)
                y_end = min(img_size, y + size)
                
                img[y_start:y_end, x_start:x_end] = [255, 140, 0]  # Orange
        
        elif 'bacterial' in disease_class.lower():
            # Add small dark spots
            num_spots = np.random.randint(15, 30)
            for _ in range(num_spots):
                x = np.random.randint(0, img_size)
                y = np.random.randint(0, img_size)
                size = np.random.randint(1, 4)
                
                x_start = max(0, x - size)
                x_end = min(img_size, x + size)
                y_start = max(0, y - size)
                y_end = min(img_size, y + size)
                
                img[y_start:y_end, x_start:x_end] = [30, 30, 30]  # Dark spots
        
        elif 'mildew' in disease_class.lower():
            # Add white powdery patches
            num_patches = np.random.randint(3, 6)
            for _ in range(num_patches):
                center_x = np.random.randint(50, img_size - 50)
                center_y = np.random.randint(50, img_size - 50)
                radius = np.random.randint(15, 25)
                
                y, x = np.ogrid[:img_size, :img_size]
                mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
                
                img[mask] = [240, 240, 240]  # White color
        
        # Add some noise for realism
        noise = np.random.normal(0, 10, img.shape)
        img = np.clip(img + noise, 0, 255).astype(np.uint8)
        
        return img
    
    def train_model(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Entraîne le modèle de détection de maladies
        """
        print("Début de l'entraînement du modèle...")
        
        # Create model
        num_classes = y.shape[1]
        self.model = self.create_efficient_model(num_classes)
        
        print(f"Architecture du modèle:")
        self.model.summary()
        
        # Prepare callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=5,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-7
            )
        ]
        
        # Train model
        history = self.model.fit(
            X, y,
            batch_size=self.model_config['batch_size'],
            epochs=self.model_config['epochs'],
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )
        
        self.training_history = history.history
        
        # Evaluate model
        final_loss, final_accuracy, final_top_k = self.model.evaluate(X, y, verbose=0)
        
        training_results = {
            'final_accuracy': final_accuracy,
            'final_loss': final_loss,
            'final_top_k_accuracy': final_top_k,
            'epochs_trained': len(history.history['loss']),
            'best_val_accuracy': max(history.history.get('val_accuracy', [0])),
            'training_time': datetime.now().isoformat(),
            'model_architecture': 'MobileNetV2_Transfer_Learning',
            'dataset_size': len(X),
            'num_classes': num_classes,
            'class_names': self.class_names
        }
        
        print(f"Entraînement terminé!")
        print(f"Précision finale: {final_accuracy:.3f}")
        print(f"Top-K précision: {final_top_k:.3f}")
        
        return training_results
    
    def fine_tune_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Fine-tune le modèle en dégelant quelques couches
        """
        if self.model is None:
            raise ValueError("Aucun modèle pré-entraîné disponible")
        
        print("Début du fine-tuning...")
        
        # Unfreeze top layers of base model
        base_model = self.model.layers[4]  # MobileNetV2 base
        base_model.trainable = True
        
        # Freeze bottom layers, unfreeze top layers
        for layer in base_model.layers[:-20]:
            layer.trainable = False
        
        # Use lower learning rate for fine-tuning
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001/10),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_k_categorical_accuracy']
        )
        
        # Fine-tune with fewer epochs
        fine_tune_epochs = 10
        history = self.model.fit(
            X, y,
            batch_size=self.model_config['batch_size'],
            epochs=fine_tune_epochs,
            validation_split=0.2,
            verbose=1
        )
        
        # Evaluate fine-tuned model
        final_loss, final_accuracy, final_top_k = self.model.evaluate(X, y, verbose=0)
        
        fine_tune_results = {
            'fine_tune_accuracy': final_accuracy,
            'fine_tune_loss': final_loss,
            'fine_tune_top_k_accuracy': final_top_k,
            'fine_tune_epochs': fine_tune_epochs,
            'fine_tune_time': datetime.now().isoformat()
        }
        
        print(f"Fine-tuning terminé! Nouvelle précision: {final_accuracy:.3f}")
        
        return fine_tune_results
    
    def save_trained_model(self, model_path: str = "models/disease_detection_model") -> bool:
        """
        Sauvegarde le modèle entraîné
        """
        try:
            if self.model is None:
                return False
            
            # Create models directory
            os.makedirs("models", exist_ok=True)
            
            # Save model
            self.model.save(f"{model_path}.h5")
            
            # Save metadata
            metadata = {
                'model_config': self.model_config,
                'class_names': self.class_names,
                'training_history': self.training_history,
                'save_date': datetime.now().isoformat(),
                'model_version': '1.0'
            }
            
            with open(f"{model_path}_metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Modèle sauvegardé: {model_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def load_trained_model(self, model_path: str = "models/disease_detection_model") -> bool:
        """
        Charge un modèle pré-entraîné
        """
        try:
            # Load model
            self.model = tf.keras.models.load_model(f"{model_path}.h5")
            
            # Load metadata
            with open(f"{model_path}_metadata.json", 'r') as f:
                metadata = json.load(f)
            
            self.class_names = metadata.get('class_names', [])
            self.model_config = metadata.get('model_config', self.model_config)
            self.training_history = metadata.get('training_history', {})
            
            print(f"Modèle chargé: {model_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return False
    
    def create_lightweight_model(self) -> tf.keras.Model:
        """
        Crée un modèle ultra-léger pour Replit
        """
        inputs = tf.keras.Input(shape=self.model_config['input_shape'])
        
        # Lightweight CNN architecture
        x = tf.keras.layers.Conv2D(32, 3, activation='relu')(inputs)
        x = tf.keras.layers.MaxPooling2D()(x)
        x = tf.keras.layers.Conv2D(64, 3, activation='relu')(x)
        x = tf.keras.layers.MaxPooling2D()(x)
        x = tf.keras.layers.Conv2D(128, 3, activation='relu')(x)
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        outputs = tf.keras.layers.Dense(len(self.class_names), activation='softmax')(x)
        
        model = tf.keras.Model(inputs, outputs)
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def benchmark_model_performance(self, test_images: List[np.ndarray]) -> Dict[str, Any]:
        """
        Benchmark des performances du modèle
        """
        if self.model is None:
            return {'error': 'Aucun modèle disponible'}
        
        start_time = datetime.now()
        
        predictions = []
        for img in test_images:
            img_batch = np.expand_dims(img, axis=0)
            pred = self.model.predict(img_batch, verbose=0)
            predictions.append(pred[0])
        
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        avg_time_per_image = processing_time / len(test_images)
        
        return {
            'total_processing_time': processing_time,
            'avg_time_per_image': avg_time_per_image,
            'images_per_second': len(test_images) / processing_time,
            'model_size_mb': self._get_model_size_mb(),
            'inference_speed': 'fast' if avg_time_per_image < 0.1 else 'moderate'
        }
    
    def _get_model_size_mb(self) -> float:
        """
        Calcule la taille du modèle en MB
        """
        if self.model is None:
            return 0
        
        try:
            # Save temporarily to get size
            temp_path = "temp_model.h5"
            self.model.save(temp_path)
            
            size_bytes = os.path.getsize(temp_path)
            size_mb = size_bytes / (1024 * 1024)
            
            # Clean up
            os.remove(temp_path)
            
            return round(size_mb, 2)
            
        except Exception:
            return 0

def quick_train_demo_model():
    """
    Entraînement rapide d'un modèle de démonstration
    """
    print("🚀 Entraînement rapide d'un modèle de démonstration...")
    
    trainer = DiseaseModelTrainer()
    
    # Generate small synthetic dataset for demo
    X, y = trainer.prepare_dataset_from_synthetic(num_samples_per_class=50)
    
    # Train with minimal epochs for demo
    trainer.model_config['epochs'] = 5
    trainer.model_config['batch_size'] = 8
    
    results = trainer.train_model(X, y)
    
    # Save model
    saved = trainer.save_trained_model("models/demo_disease_model")
    
    if saved:
        print("✅ Modèle de démonstration entraîné et sauvegardé!")
        print(f"Précision: {results['final_accuracy']:.3f}")
        print(f"Classes supportées: {len(trainer.class_names)}")
    
    return trainer, results

if __name__ == "__main__":
    # Run demo training
    quick_train_demo_model()
