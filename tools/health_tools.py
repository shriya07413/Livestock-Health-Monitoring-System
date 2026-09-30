"""
Health Tools for AI Agents
============================
These tools help agents perform health-related calculations and assessments.

These tools contain domain knowledge about livestock health parameters
like normal temperature ranges and weight expectations.
"""

from utils.config import get_temp_range, get_weight_range, APP_CONFIG
from utils.helpers import get_current_datetime, parse_symptoms


def calculate_health_metrics(animal_type, weight, temperature, symptoms_text,
                             food_intake="Normal", water_intake="Normal",
                             activity_level="Normal"):
    """
    TOOL: Calculate health metrics and determine health status.
    
    This tool analyzes the provided health parameters and returns
    a structured assessment. It compares values against known
    normal ranges for the specific animal type.
    
    The Health Analysis Agent uses this tool to perform its analysis.
    
    Args:
        animal_type (str): Type of animal
        weight (float): Weight in kg
        temperature (float): Body temperature in °C
        symptoms_text (str): Reported symptoms
        food_intake (str): Food consumption level
        water_intake (str): Water consumption level
        activity_level (str): Activity level
    
    Returns:
        dict: Health metrics including status, warnings, and scores
    """
    warnings = []
    risk_score = 0  # 0 = healthy, higher = more concern
    
    # --- Temperature Analysis ---
    temp_min, temp_max = get_temp_range(animal_type)
    temp_status = "Normal"
    
    try:
        temp = float(temperature)
        if temp < temp_min:
            temp_status = "Below Normal (Hypothermia risk)"
            warnings.append(f"🌡️ Temperature ({temp}°C) is below normal range ({temp_min}-{temp_max}°C)")
            risk_score += 2
        elif temp > temp_max:
            diff = temp - temp_max
            if diff > 1.5:
                temp_status = "High Fever"
                warnings.append(f"🌡️ HIGH FEVER: Temperature ({temp}°C) is significantly above normal ({temp_min}-{temp_max}°C)")
                risk_score += 4
            else:
                temp_status = "Mild Fever"
                warnings.append(f"🌡️ Mild fever: Temperature ({temp}°C) is above normal ({temp_min}-{temp_max}°C)")
                risk_score += 2
        else:
            pass  # Temperature is normal
    except (ValueError, TypeError):
        temp_status = "Unable to assess"
        warnings.append("⚠️ Could not evaluate temperature - invalid value provided")
    
    # --- Weight Analysis ---
    weight_min, weight_max = get_weight_range(animal_type)
    weight_status = "Normal"
    
    try:
        w = float(weight)
        if w > 0:
            if w < weight_min * 0.7:
                weight_status = "Severely Underweight"
                warnings.append(f"⚖️ Weight ({w}kg) is severely below expected range ({weight_min}-{weight_max}kg)")
                risk_score += 3
            elif w < weight_min:
                weight_status = "Underweight"
                warnings.append(f"⚖️ Weight ({w}kg) is below expected range ({weight_min}-{weight_max}kg)")
                risk_score += 1
            elif w > weight_max * 1.3:
                weight_status = "Severely Overweight"
                warnings.append(f"⚖️ Weight ({w}kg) is significantly above expected range ({weight_min}-{weight_max}kg)")
                risk_score += 2
            elif w > weight_max:
                weight_status = "Overweight"
                warnings.append(f"⚖️ Weight ({w}kg) is above expected range ({weight_min}-{weight_max}kg)")
                risk_score += 1
    except (ValueError, TypeError):
        weight_status = "Unable to assess"
    
    # --- Symptoms Analysis ---
    symptoms_list = parse_symptoms(symptoms_text)
    symptom_count = len(symptoms_list)
    
    # Check for concerning symptoms
    serious_keywords = [
        "blood", "bleeding", "collapse", "unconscious", "seizure",
        "not breathing", "paralysis", "severe", "sudden death",
        "swelling", "bloating", "diarrhea", "vomiting"
    ]
    
    moderate_keywords = [
        "not eating", "loss of appetite", "weakness", "lethargy",
        "coughing", "discharge", "limping", "lameness",
        "reduced milk", "weight loss", "fever", "dull coat"
    ]
    
    for symptom in symptoms_list:
        symptom_lower = symptom.lower()
        for keyword in serious_keywords:
            if keyword in symptom_lower:
                risk_score += 3
                warnings.append(f"🚨 Serious symptom detected: {symptom}")
                break
        for keyword in moderate_keywords:
            if keyword in symptom_lower:
                risk_score += 1.5
                break
    
    # Risk from number of symptoms
    if symptom_count >= 4:
        risk_score += 2
        warnings.append("⚠️ Multiple symptoms reported - comprehensive evaluation recommended")
    elif symptom_count >= 2:
        risk_score += 1
    
    # --- Behavioral Analysis ---
    if food_intake.lower() in ("reduced", "very low", "none", "not eating"):
        risk_score += 2
        warnings.append("🍽️ Reduced food intake reported")
    
    if water_intake.lower() in ("reduced", "very low", "none", "not drinking"):
        risk_score += 2
        warnings.append("💧 Reduced water intake reported - dehydration risk")
    
    if activity_level.lower() in ("very low", "reduced", "lethargic"):
        risk_score += 1.5
        warnings.append("🏃 Reduced activity level reported")
    
    # --- Determine Overall Health Status ---
    if risk_score == 0:
        health_status = "Healthy"
        status_emoji = "🟢"
    elif risk_score <= 3:
        health_status = "Needs Monitoring"
        status_emoji = "🟡"
    elif risk_score <= 6:
        health_status = "Warning"
        status_emoji = "🟠"
    else:
        health_status = "Critical"
        status_emoji = "🔴"
        warnings.append("🚨 URGENT: Multiple concerning indicators detected. "
                        "Please consult a veterinarian immediately.")
    
    return {
        "health_status": health_status,
        "status_emoji": status_emoji,
        "risk_score": round(risk_score, 1),
        "temperature_status": temp_status,
        "weight_status": weight_status,
        "normal_temp_range": f"{temp_min}-{temp_max}°C",
        "normal_weight_range": f"{weight_min}-{weight_max}kg",
        "symptom_count": symptom_count,
        "symptoms_list": symptoms_list,
        "warnings": warnings,
        "warning_count": len(warnings),
        "food_intake": food_intake,
        "water_intake": water_intake,
        "activity_level": activity_level,
        "assessed_at": get_current_datetime(),
    }


def get_health_knowledge(animal_type, topic="general"):
    """
    TOOL: Retrieve basic livestock health knowledge.
    
    This is a simple knowledge retrieval tool that provides
    domain-specific information about livestock health.
    
    Args:
        animal_type (str): Type of animal
        topic (str): Topic area (general, feeding, common_diseases, vaccination)
    
    Returns:
        dict: Knowledge information
    """
    # Basic health knowledge base
    knowledge_base = {
        "cow": {
            "general": (
                "Cows should have a normal temperature of 37.8-39.2°C. "
                "Normal resting heart rate is 48-84 bpm. "
                "Normal respiratory rate is 26-50 breaths/min. "
                "A healthy cow should have a shiny coat, clear eyes, "
                "good appetite, and normal activity levels."
            ),
            "feeding": (
                "Adult cows typically consume 2-3% of their body weight in "
                "dry matter daily. Fresh clean water should be available at all times. "
                "A balanced diet should include roughage (hay, silage), "
                "concentrates (grains), minerals, and vitamins. "
                "Lactating cows need additional nutrition."
            ),
            "common_diseases": (
                "Common cattle diseases include: Mastitis, Foot-and-Mouth Disease, "
                "Bovine Respiratory Disease, Bloat, Milk Fever, Ketosis, "
                "Johne's Disease, and various parasitic infections."
            ),
            "vaccination": (
                "Common vaccinations for cattle include: FMD (Foot and Mouth Disease), "
                "Black Quarter, Hemorrhagic Septicemia, Brucellosis, "
                "and Theileriosis. Consult a local veterinarian for "
                "the recommended vaccination schedule in your area."
            ),
        },
        "goat": {
            "general": (
                "Goats should have a normal temperature of 38.5-39.7°C. "
                "Normal heart rate is 70-95 bpm. "
                "Normal respiratory rate is 12-20 breaths/min. "
                "Healthy goats are active, curious, and have good appetites."
            ),
            "feeding": (
                "Goats are browsers and prefer a varied diet. "
                "They need roughage, browse, and may need supplemental grains. "
                "Fresh, clean water should always be available. "
                "Adult goats eat about 3-4% of body weight daily."
            ),
            "common_diseases": (
                "Common goat diseases include: PPR (Peste des Petits Ruminants), "
                "Enterotoxemia, Pneumonia, Parasitic infections (worms), "
                "Foot Rot, and Mastitis."
            ),
            "vaccination": (
                "Common vaccinations for goats include: PPR, Enterotoxemia, "
                "Foot-and-Mouth Disease, and Goat Pox. "
                "Consult a veterinarian for local recommendations."
            ),
        },
        "buffalo": {
            "general": (
                "Buffaloes should have a normal temperature of 37.5-39.0°C. "
                "They are more susceptible to heat stress than cattle. "
                "Healthy buffaloes have a good appetite, shiny coat, "
                "and are alert and active."
            ),
            "feeding": (
                "Buffaloes require a diet similar to cattle but with "
                "attention to their specific nutritional needs. "
                "They need good quality roughage, concentrates, "
                "and mineral supplements. Lactating buffaloes need "
                "additional energy and protein."
            ),
            "common_diseases": (
                "Common buffalo diseases include: Hemorrhagic Septicemia, "
                "Foot-and-Mouth Disease, Brucellosis, "
                "Parasitic infections, and Mastitis."
            ),
            "vaccination": (
                "Key vaccinations include: FMD, HS (Hemorrhagic Septicemia), "
                "BQ (Black Quarter), and Brucellosis. "
                "Follow the local veterinary calendar."
            ),
        },
        "sheep": {
            "general": (
                "Sheep should have a normal temperature of 38.3-39.9°C. "
                "Normal heart rate is 70-80 bpm. "
                "Healthy sheep are alert, have clear eyes, "
                "clean nostrils, and normal droppings."
            ),
            "feeding": (
                "Sheep primarily eat grass and hay. They need access to "
                "clean water and mineral supplements. Pregnant and "
                "lactating ewes need additional nutrition. "
                "Adult sheep eat about 2-4% of body weight daily."
            ),
            "common_diseases": (
                "Common sheep diseases include: Foot Rot, Pneumonia, "
                "Enterotoxemia, Internal parasites, Sheep Pox, "
                "and Pregnancy Toxemia."
            ),
            "vaccination": (
                "Common vaccinations for sheep include: Enterotoxemia, "
                "Sheep Pox, PPR, FMD, and Blue Tongue. "
                "Consult a veterinarian for the local schedule."
            ),
        },
    }
    
    # Get knowledge for the specified animal
    animal_key = animal_type.lower().strip()
    
    if animal_key in knowledge_base:
        animal_knowledge = knowledge_base[animal_key]
        if topic in animal_knowledge:
            return {
                "found": True,
                "animal_type": animal_type,
                "topic": topic,
                "information": animal_knowledge[topic]
            }
        else:
            return {
                "found": True,
                "animal_type": animal_type,
                "topic": "general",
                "information": animal_knowledge.get("general", "No specific information available.")
            }
    else:
        return {
            "found": False,
            "animal_type": animal_type,
            "topic": topic,
            "information": (
                f"Specific health knowledge for {animal_type} is limited in this system. "
                "General livestock health principles apply: monitor temperature, "
                "appetite, water intake, activity level, and any unusual symptoms. "
                "Consult a veterinarian for species-specific guidance."
            )
        }
