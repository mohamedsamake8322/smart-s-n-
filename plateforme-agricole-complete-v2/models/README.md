# Modèles d'IA Agricole

Ce dossier contient les modèles d'intelligence artificielle pré-entraînés pour la prédiction de rendement agricole.

## Modèles Disponibles

### 1. Random Forest Regressor
- **Fichier**: `random_forest_model.joblib`
- **Performance**: R² Score > 0.85
- **Utilisation**: Prédiction générale de rendement
- **Avantages**: Robuste aux valeurs aberrantes, interprétable

### 2. XGBoost Regressor
- **Fichier**: `xgboost_model.joblib`
- **Performance**: R² Score > 0.90
- **Utilisation**: Prédictions haute précision
- **Avantages**: Performance supérieure, gestion automatique des features

### 3. Linear Regression
- **Fichier**: `linear_regression_model.joblib`
- **Performance**: R² Score > 0.75
- **Utilisation**: Baseline et interprétation simple
- **Avantages**: Rapide, simple à comprendre

## Encodeurs et Preprocesseurs

### Encodeurs Catégoriels
- `crop_type_encoder.joblib`: Encodage des types de cultures
- `field_encoder.joblib`: Encodage des identifiants de champs

### Scalers
- `feature_scaler.joblib`: Normalisation des features numériques
- `target_scaler.joblib`: Normalisation des variables cibles

## Utilisation

```python
import joblib
from utils.ml_models import YieldPredictor

# Charger un modèle
predictor = YieldPredictor()
predictor.load_model('models/random_forest_model.joblib')

# Faire une prédiction
prediction = predictor.predict(input_data)
```

## Métriques de Performance

| Modèle | R² Score | MAE | RMSE |
|--------|----------|-----|------|
| Random Forest | 0.87 | 0.45 | 0.63 |
| XGBoost | 0.92 | 0.38 | 0.52 |
| Linear Regression | 0.76 | 0.68 | 0.89 |

## Mise à Jour des Modèles

Les modèles sont automatiquement sauvegardés après chaque entraînement dans l'interface utilisateur.