"""
Helper Utilities for Livestock Health Monitoring Assistant
==========================================================
This module contains helper functions used across the application.
These are general-purpose utilities that don't belong to any specific agent.
"""

from datetime import datetime
import json
import re


def get_current_datetime():
    """
    Get the current date and time as a formatted string.
    
    Returns:
        str: Current date and time (e.g., "2024-03-15 14:30:45")
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_date():
    """
    Get the current date as a formatted string.
    
    Returns:
        str: Current date (e.g., "2024-03-15")
    """
    return datetime.now().strftime("%Y-%m-%d")


def generate_animal_id(animal_type, existing_count):
    """
    Generate a unique animal ID based on the animal type.
    
    Example: COW-001, GOAT-002, etc.
    
    Args:
        animal_type (str): Type of animal
        existing_count (int): Number of existing animals of this type
    
    Returns:
        str: Generated animal ID
    """
    prefix = animal_type.upper()[:3]
    number = existing_count + 1
    return f"{prefix}-{number:03d}"


def validate_temperature(temp_str):
    """
    Validate and parse a temperature value.
    
    Args:
        temp_str (str or float): Temperature value
    
    Returns:
        tuple: (is_valid, temperature_float, error_message)
    """
    try:
        temp = float(str(temp_str).replace("°C", "").replace("°F", "").strip())
        if temp < 30 or temp > 45:
            return False, temp, f"Temperature {temp}°C seems unusual. Normal range is 37-41°C."
        return True, temp, ""
    except (ValueError, TypeError):
        return False, 0.0, "Please enter a valid number for temperature."


def validate_weight(weight_str):
    """
    Validate and parse a weight value.
    
    Args:
        weight_str (str or float): Weight value in kg
    
    Returns:
        tuple: (is_valid, weight_float, error_message)
    """
    try:
        weight = float(str(weight_str).replace("kg", "").replace("KG", "").strip())
        if weight <= 0:
            return False, weight, "Weight must be a positive number."
        if weight > 2000:
            return False, weight, "Weight seems unusually high. Please check."
        return True, weight, ""
    except (ValueError, TypeError):
        return False, 0.0, "Please enter a valid number for weight."


def format_health_status(status):
    """
    Format health status with appropriate emoji indicators.
    
    Args:
        status (str): Health status
    
    Returns:
        str: Formatted status with emoji
    """
    status_map = {
        "healthy": "🟢 Healthy",
        "normal": "🟢 Normal",
        "monitor": "🟡 Needs Monitoring",
        "needs monitoring": "🟡 Needs Monitoring",
        "warning": "🟠 Warning",
        "critical": "🔴 Critical",
        "unknown": "⚪ Unknown",
    }
    return status_map.get(status.lower().strip(), f"⚪ {status}")


def parse_symptoms(symptoms_text):
    """
    Parse symptoms text into a clean list.
    
    Args:
        symptoms_text (str): Raw symptoms text from user
    
    Returns:
        list: List of individual symptoms
    """
    if not symptoms_text or symptoms_text.strip() == "":
        return []
    
    # Split by common delimiters
    # Users might separate symptoms with commas, newlines, semicolons, or "and"
    symptoms = re.split(r'[,;\n]+|(?:\band\b)', symptoms_text)
    
    # Clean up each symptom
    cleaned = []
    for symptom in symptoms:
        s = symptom.strip()
        if s and len(s) > 1:  # Ignore empty or single-character entries
            cleaned.append(s)
    
    return cleaned


def calculate_age_in_months(age_str):
    """
    Convert an age string to months for comparison.
    
    Supports formats like: "2 years", "6 months", "3", "1.5 years"
    
    Args:
        age_str (str): Age as text
    
    Returns:
        float: Age in months, or -1 if parsing fails
    """
    try:
        age_str = str(age_str).lower().strip()
        
        # Try to extract number and unit
        match = re.match(r'([\d.]+)\s*(year|yr|month|mon|week|wk|day)?s?', age_str)
        if match:
            value = float(match.group(1))
            unit = match.group(2) or "year"  # Default to years
            
            if unit in ("year", "yr"):
                return value * 12
            elif unit in ("month", "mon"):
                return value
            elif unit in ("week", "wk"):
                return value / 4.33
            elif unit == "day":
                return value / 30.44
        
        # If no unit found, try parsing as a plain number (assume years)
        return float(age_str) * 12
    except (ValueError, TypeError, AttributeError):
        return -1


def format_record_for_display(record):
    """
    Format a database record dictionary into a readable string.
    
    Args:
        record (dict): Health record from database
    
    Returns:
        str: Formatted string for display
    """
    if not record:
        return "No record found."
    
    lines = []
    lines.append(f"📋 **Animal ID:** {record.get('animal_id', 'N/A')}")
    lines.append(f"🐄 **Type:** {record.get('animal_type', 'N/A')}")
    lines.append(f"📅 **Breed:** {record.get('breed', 'N/A')}")
    lines.append(f"📅 **Age:** {record.get('age', 'N/A')}")
    lines.append(f"⚥ **Gender:** {record.get('gender', 'N/A')}")
    lines.append(f"⚖️ **Weight:** {record.get('weight', 'N/A')} kg")
    lines.append(f"🌡️ **Temperature:** {record.get('temperature', 'N/A')}°C")
    lines.append(f"🍽️ **Food Intake:** {record.get('food_intake', 'N/A')}")
    lines.append(f"💧 **Water Intake:** {record.get('water_intake', 'N/A')}")
    lines.append(f"🏃 **Activity Level:** {record.get('activity_level', 'N/A')}")
    lines.append(f"🤒 **Symptoms:** {record.get('symptoms', 'None reported')}")
    lines.append(f"📊 **Health Status:** {format_health_status(record.get('health_status', 'unknown'))}")
    lines.append(f"📅 **Date:** {record.get('created_at', 'N/A')}")
    
    return "\n".join(lines)


def safe_json_loads(text, default=None):
    """
    Safely parse JSON text, returning a default value if parsing fails.
    
    Args:
        text (str): JSON text to parse
        default: Default value if parsing fails
    
    Returns:
        Parsed JSON data or default value
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}
