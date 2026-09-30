"""
Configuration Module for Livestock Health Monitoring Assistant
==============================================================
This module handles:
- Loading environment variables (like the API key)
- Setting up configuration for the entire application
- Managing demo mode when no API key is available

WHY THIS FILE EXISTS:
Instead of putting the API key directly in the code (which is UNSAFE),
we read it from a .env file. This keeps the key secret.
"""

import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_api_key():
    """
    Get the OpenAI API key from environment variables.
    
    HOW IT WORKS:
    1. First, it checks if there's a .env file with OPENAI_API_KEY
    2. If found, it returns the key
    3. If not found, it returns None (which triggers demo mode)
    
    Returns:
        str or None: The API key, or None if not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Check if the key is actually set (not just the placeholder)
    if api_key and api_key != "your_api_key_here" and len(api_key) > 10:
        return api_key
    
    return None


def is_demo_mode():
    """
    Check if the application is running in demo mode.
    
    Demo mode is activated when:
    - No API key is provided
    - The API key is the default placeholder
    
    In demo mode, the app works with pre-written responses
    instead of calling the real AI API.
    
    Returns:
        bool: True if running in demo mode, False otherwise
    """
    return get_api_key() is None


# -------------------------------------------------------------------
# Application Configuration
# -------------------------------------------------------------------
# These are settings used throughout the application

APP_CONFIG = {
    "app_name": "🐄 Livestock Health Monitoring Assistant",
    "app_subtitle": "AI-powered livestock health monitoring and intelligent assistance",
    "version": "1.0.0",
    
    # OpenAI model to use (gpt-3.5-turbo is cheaper and works well)
    "model": "gpt-4o-mini",
    
    # Maximum tokens (length) for AI responses
    "max_tokens": 2000,
    
    # Temperature controls randomness (0 = focused, 1 = creative)
    "temperature": 0.3,
    
    # Database file path
    "database_path": os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   "database", "livestock.db"),
    
    # Reports directory
    "reports_dir": os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                "reports"),
    
    # Charts directory
    "charts_dir": os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                               "charts"),
    
    # Safety disclaimer that appears in every health analysis
    "safety_disclaimer": (
        "⚠️ IMPORTANT DISCLAIMER: This system provides AI-assisted health "
        "monitoring for educational and informational purposes only. It does "
        "NOT replace professional veterinary diagnosis or treatment. Always "
        "consult a qualified veterinarian for medical decisions regarding "
        "your livestock."
    ),
    
    # Normal temperature ranges for different animals (in °C)
    "normal_temp_ranges": {
        "cow": (37.8, 39.2),
        "buffalo": (37.5, 39.0),
        "goat": (38.5, 39.7),
        "sheep": (38.3, 39.9),
        "horse": (37.5, 38.5),
        "pig": (38.0, 39.5),
        "chicken": (40.6, 41.7),
        "default": (37.5, 39.5),
    },
    
    # Normal weight ranges (in kg) - approximate
    "normal_weight_ranges": {
        "cow": (300, 900),
        "buffalo": (350, 1000),
        "goat": (20, 80),
        "sheep": (25, 100),
        "horse": (380, 600),
        "pig": (50, 350),
        "chicken": (1, 5),
        "default": (10, 500),
    },
}


# -------------------------------------------------------------------
# Animal Types supported by the system
# -------------------------------------------------------------------
ANIMAL_TYPES = ["Cow", "Buffalo", "Goat", "Sheep", "Horse", "Pig", "Chicken", "Other"]

# Activity levels
ACTIVITY_LEVELS = ["Normal", "Reduced", "Very Low", "Hyperactive", "Unknown"]

# Gender options
GENDER_OPTIONS = ["Male", "Female", "Unknown"]


def get_temp_range(animal_type):
    """
    Get the normal temperature range for a given animal type.
    
    Args:
        animal_type (str): Type of animal (e.g., "cow", "goat")
    
    Returns:
        tuple: (min_temp, max_temp) in Celsius
    """
    animal = animal_type.lower().strip()
    return APP_CONFIG["normal_temp_ranges"].get(
        animal, APP_CONFIG["normal_temp_ranges"]["default"]
    )


def get_weight_range(animal_type):
    """
    Get the normal weight range for a given animal type.
    
    Args:
        animal_type (str): Type of animal (e.g., "cow", "goat")
    
    Returns:
        tuple: (min_weight, max_weight) in kg
    """
    animal = animal_type.lower().strip()
    return APP_CONFIG["normal_weight_ranges"].get(
        animal, APP_CONFIG["normal_weight_ranges"]["default"]
    )
