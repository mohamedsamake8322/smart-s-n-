def validate_input(crop, pH, soil_type, growth_stage, temperature, humidity):
    """ Vérifie que les entrées utilisateur sont valides avec des critères avancés. """
    
    # 📌 Vérification de valeurs manquantes
    if not crop or not soil_type or not growth_stage:
        return False, "🚨 Missing crop, soil type, or growth stage!"
    
    # 📌 Vérification du pH selon la culture
    optimal_pH_ranges = {
        "Maize": (5.8, 7.5),
        "Millet": (5.5, 7.5),
        "Rice": (5.0, 7.5),
        "Sorghum": (5.5, 7.5),
        "Tomato": (5.5, 7.5),
        "Okra": (6.0, 7.5)
    }

    if pH < 3.5 or pH > 9.0:
        return False, "🚨 pH out of acceptable range (3.5 - 9.0)!"
    
    if crop in optimal_pH_ranges and not (optimal_pH_ranges[crop][0] <= pH <= optimal_pH_ranges[crop][1]):
        return False, f"🚨 Warning: The pH is outside the recommended range for {crop} ({optimal_pH_ranges[crop][0]} - {optimal_pH_ranges[crop][1]})."

    # 📌 Vérification de la température
    if temperature < -10 or temperature > 50:
        return False, "🚨 Temperature seems unrealistic!"

    optimal_temp_ranges = {
        "Maize": (18, 30),
        "Millet": (20, 35),
        "Rice": (22, 32),
        "Sorghum": (18, 32),
        "Tomato": (18, 25),
        "Okra": (20, 30)
    }

    if crop in optimal_temp_ranges and not (optimal_temp_ranges[crop][0] <= temperature <= optimal_temp_ranges[crop][1]):
        return False, f"🚨 Warning: The temperature is outside the ideal range for {crop} ({optimal_temp_ranges[crop][0]} - {optimal_temp_ranges[crop][1]})."

    # 📌 Vérification du taux d’humidité
    if humidity < 0 or humidity > 100:
        return False, "🚨 Humidity percentage must be between 0-100!"

    optimal_humidity_ranges = {
        "Maize": (60, 80),
        "Millet": (50, 75),
        "Rice": (70, 90),
        "Sorghum": (50, 70),
        "Tomato": (60, 80),
        "Okra": (55, 75)
    }

    if crop in optimal_humidity_ranges and not (optimal_humidity_ranges[crop][0] <= humidity <= optimal_humidity_ranges[crop][1]):
        return False, f"🚨 Warning: The humidity is outside the ideal range for {crop} ({optimal_humidity_ranges[crop][0]} - {optimal_humidity_ranges[crop][1]})."

    # 📌 Vérification des associations sol/culture
    incompatible_soil_types = {
        "Rice": ["Sandy"],
        "Tomato": ["Clay"],
        "Maize": ["Clay"]
    }

    if crop in incompatible_soil_types and soil_type in incompatible_soil_types[crop]:
        return False, f"🚨 Warning: {crop} does not grow well in {soil_type} soil!"

    # 📌 Avertissement sur les maladies potentielles
    disease_risk_factors = {
        "Rice": ["High Humidity (>85%) → Rice Blast Disease"],
        "Tomato": ["High Humidity (>80%) & Warm Temp → Powdery Mildew"],
        "Maize": ["Low pH (<5.5) → Fusarium Wilt"]
    }

    warnings = []
    if crop in disease_risk_factors:
        for condition in disease_risk_factors[crop]:
            if "Humidity" in condition and humidity > 85:
                warnings.append(condition)
            elif "Temp" in condition and temperature > 30:
                warnings.append(condition)
            elif "Low pH" in condition and pH < 5.5:
                warnings.append(condition)

    # 📌 Retour avec avertissements si nécessaire
    if warnings:
        return True, f"⚠️ Potential Disease Risk: {', '.join(warnings)}"

    return True, None  # ✅ Tout est valide
