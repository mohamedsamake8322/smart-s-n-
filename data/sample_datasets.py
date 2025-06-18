"""
GÃ©nÃ©rateur de jeux de donnÃ©es d'exemple pour dÃ©monstration
Note: Ces donnÃ©es sont uniquement pour les tests et dÃ©monstrations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def create_agricultural_sample_dataset():
    """GÃ©nÃ¨re un jeu de donnÃ©es agricoles d'exemple"""
    np.random.seed(42)
    
    crop_types = ['BlÃ©', 'MaÃ¯s', 'Riz', 'Soja', 'Orge', 'Coton', 'Tournesol', 'Colza']
    regions = ['Normandie', 'Bretagne', 'Beauce', 'Champagne', 'Bourgogne', 'Picardie']
    
    n_samples = 500
    
    data = []
    for i in range(n_samples):
        # DonnÃ©es de base
        crop = np.random.choice(crop_types)
        region = np.random.choice(regions)
        
        # ParamÃ¨tres environnementaux
        temperature = np.random.normal(20, 6)
        rainfall = np.random.exponential(400)
        humidity = np.random.normal(65, 12)
        soil_ph = np.random.normal(6.5, 0.8)
        soil_nitrogen = np.random.normal(45, 15)
        soil_phosphorus = np.random.normal(25, 8)
        soil_potassium = np.random.normal(180, 40)
        
        # Surface cultivÃ©e
        area = np.random.uniform(5, 100)
        
        # Calcul du rendement basÃ© sur les conditions
        base_yields = {
            'BlÃ©': 7.2, 'MaÃ¯s': 10.5, 'Riz': 8.8, 'Soja': 3.2,
            'Orge': 6.8, 'Coton': 2.1, 'Tournesol': 2.8, 'Colza': 3.5
        }
        
        base_yield = base_yields[crop]
        
        # Facteurs d'ajustement
        temp_factor = 1.0 if 15 <= temperature <= 25 else 0.85
        rain_factor = 1.0 if 300 <= rainfall <= 700 else 0.9
        ph_factor = 1.0 if 6.0 <= soil_ph <= 7.5 else 0.88
        nitrogen_factor = min(1.2, soil_nitrogen / 40)
        
        # Calcul final avec variabilitÃ©
        yield_value = base_yield * temp_factor * rain_factor * ph_factor * nitrogen_factor
        yield_value *= np.random.normal(1.0, 0.15)  # VariabilitÃ© naturelle
        yield_value = max(0.5, yield_value)  # Minimum rÃ©aliste
        
        # DonnÃ©es Ã©conomiques
        cost_per_hectare = np.random.uniform(800, 1800)
        price_per_ton = np.random.uniform(180, 450)
        total_cost = cost_per_hectare * area
        total_revenue = yield_value * area * price_per_ton
        profit = total_revenue - total_cost
        
        # Date de rÃ©colte
        harvest_date = datetime.now() - timedelta(days=np.random.randint(0, 365))
        
        record = {
            'id': i + 1,
            'crop_type': crop,
            'region': region,
            'area': round(area, 2),
            'yield': round(yield_value, 2),
            'temperature': round(temperature, 1),
            'rainfall': round(rainfall, 1),
            'humidity': round(humidity, 1),
            'soil_ph': round(soil_ph, 2),
            'soil_nitrogen': round(soil_nitrogen, 1),
            'soil_phosphorus': round(soil_phosphorus, 1),
            'soil_potassium': round(soil_potassium, 1),
            'cost': round(total_cost, 2),
            'revenue': round(total_revenue, 2),
            'profit': round(profit, 2),
            'harvest_date': harvest_date.strftime('%Y-%m-%d'),
            'quality_grade': np.random.choice(['A', 'B', 'C'], p=[0.3, 0.5, 0.2])
        }
        data.append(record)
    
    return pd.DataFrame(data)

def create_weather_sample_dataset():
    """GÃ©nÃ¨re un jeu de donnÃ©es mÃ©tÃ©orologiques d'exemple"""
    np.random.seed(42)
    
    # 365 jours de donnÃ©es mÃ©tÃ©o
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range(365)]
    
    data = []
    for date in dates:
        # Variation saisonniÃ¨re
        day_of_year = date.timetuple().tm_yday
        seasonal_temp = 15 + 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # DonnÃ©es mÃ©tÃ©o avec variabilitÃ©
        temperature = seasonal_temp + np.random.normal(0, 5)
        humidity = np.random.normal(65, 15)
        rainfall = np.random.exponential(2) if np.random.random() < 0.3 else 0
        wind_speed = np.random.normal(15, 8)
        pressure = np.random.normal(1013, 20)
        uv_index = max(0, np.random.normal(5, 3))
        
        # Conditions mÃ©tÃ©o
        if rainfall > 10:
            condition = 'Pluvieux'
        elif humidity > 80:
            condition = 'Nuageux'
        elif temperature > 25:
            condition = 'EnsoleillÃ©'
        else:
            condition = 'Partiellement nuageux'
        
        record = {
            'date': date.strftime('%Y-%m-%d'),
            'temperature': round(temperature, 1),
            'humidity': round(max(0, min(100, humidity)), 1),
            'rainfall': round(max(0, rainfall), 1),
            'wind_speed': round(max(0, wind_speed), 1),
            'pressure': round(pressure, 1),
            'uv_index': round(max(0, uv_index), 1),
            'condition': condition
        }
        data.append(record)
    
    return pd.DataFrame(data)

def create_soil_sample_dataset():
    """GÃ©nÃ¨re un jeu de donnÃ©es de surveillance du sol d'exemple"""
    np.random.seed(42)
    
    field_ids = ['Champ_A', 'Champ_B', 'Champ_C', 'Champ_D', 'Champ_E']
    
    # 30 jours de donnÃ©es pour chaque champ
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data = []
    for field_id in field_ids:
        # CaractÃ©ristiques de base du champ
        base_ph = np.random.normal(6.5, 0.5)
        base_nitrogen = np.random.normal(45, 10)
        base_phosphorus = np.random.normal(25, 5)
        base_potassium = np.random.normal(180, 30)
        
        for day in range(31):
            date = start_date + timedelta(days=day)
            
            # Variations journaliÃ¨res
            ph = base_ph + np.random.normal(0, 0.2)
            moisture = np.random.normal(55, 12)
            temperature = np.random.normal(18, 4)
            conductivity = np.random.normal(1.2, 0.3)
            
            # Nutriments avec tendances
            nitrogen = base_nitrogen + np.random.normal(0, 3)
            phosphorus = base_phosphorus + np.random.normal(0, 2)
            potassium = base_potassium + np.random.normal(0, 10)
            organic_matter = np.random.normal(3.5, 0.8)
            
            record = {
                'field_id': field_id,
                'date': date.strftime('%Y-%m-%d'),
                'ph': round(max(4, min(9, ph)), 2),
                'moisture': round(max(10, min(90, moisture)), 1),
                'temperature': round(temperature, 1),
                'conductivity': round(max(0.5, conductivity), 2),
                'nitrogen': round(max(0, nitrogen), 1),
                'phosphorus': round(max(0, phosphorus), 1),
                'potassium': round(max(0, potassium), 1),
                'organic_matter': round(max(1, organic_matter), 2)
            }
            data.append(record)
    
    return pd.DataFrame(data)

def export_all_sample_datasets():
    """Exporte tous les jeux de donnÃ©es d'exemple"""
    
    # CrÃ©ation des datasets
    agricultural_data = create_agricultural_sample_dataset()
    weather_data = create_weather_sample_dataset()
    soil_data = create_soil_sample_dataset()
    
    # Export CSV
    agricultural_data.to_csv('agricultural_sample_data.csv', index=False)
    weather_data.to_csv('weather_sample_data.csv', index=False)
    soil_data.to_csv('soil_sample_data.csv', index=False)
    
    # Export JSON
    agricultural_data.to_json('agricultural_sample_data.json', orient='records', indent=2)
    weather_data.to_json('weather_sample_data.json', orient='records', indent=2)
    soil_data.to_json('soil_sample_data.json', orient='records', indent=2)
    
    # Export Excel
    with pd.ExcelWriter('complete_agricultural_dataset.xlsx') as writer:
        agricultural_data.to_excel(writer, sheet_name='DonnÃ©es Agricoles', index=False)
        weather_data.to_excel(writer, sheet_name='DonnÃ©es MÃ©tÃ©o', index=False)
        soil_data.to_excel(writer, sheet_name='DonnÃ©es Sol', index=False)
    
    print("Tous les jeux de donnÃ©es d'exemple ont Ã©tÃ© exportÃ©s avec succÃ¨s!")
    return {
        'agricultural': len(agricultural_data),
        'weather': len(weather_data), 
        'soil': len(soil_data)
    }

if __name__ == "__main__":
    stats = export_all_sample_datasets()
    print(f"Statistiques des exports:")
    print(f"- DonnÃ©es agricoles: {stats['agricultural']} enregistrements")
    print(f"- DonnÃ©es mÃ©tÃ©o: {stats['weather']} enregistrements")
    print(f"- DonnÃ©es sol: {stats['soil']} enregistrements")




