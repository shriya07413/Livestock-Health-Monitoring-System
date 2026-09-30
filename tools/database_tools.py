"""
Database Tools for AI Agents
==============================
These are the "tools" that AI agents use to interact with the database.

WHAT ARE TOOLS IN AGENTIC AI?
Tools are functions that AI agents can call to perform specific tasks.
Instead of the AI doing everything on its own, it can use tools to:
- Save data to a database
- Read information
- Perform calculations
- Generate charts

Think of tools like apps on your phone - each tool does one specific job.

In this project, database tools help agents save and retrieve animal data.
"""

from database.database import LivestockDatabase
from utils.helpers import get_current_datetime


# Create a single database instance to be shared by all agents
db = LivestockDatabase()


def save_health_record(record_data):
    """
    TOOL: Save a health record to the database.
    
    This tool is used by the Health Analysis Agent after it finishes
    analyzing an animal's health. It stores all the information so
    it can be retrieved later.
    
    AGENTIC AI CONCEPT:
    This is a "tool" that agents can "call" to perform actions.
    The agent decides WHEN to use this tool based on the situation.
    
    Args:
        record_data (dict): Dictionary with health record fields:
            - animal_id: Unique ID of the animal
            - animal_type: Type (Cow, Goat, etc.)
            - breed: Breed of the animal
            - age: Age
            - gender: Gender
            - weight: Weight in kg
            - temperature: Body temperature in °C
            - symptoms: Reported symptoms
            - food_intake: Food consumption level
            - water_intake: Water consumption level
            - activity_level: Activity level
            - additional_notes: Any extra notes
            - health_status: Overall health status
            - health_analysis: AI-generated health analysis
            - nutrition_advice: AI-generated nutrition advice
            - monitoring_notes: Monitoring observations
    
    Returns:
        dict: Result with success status and message
    """
    try:
        success, message, record_id = db.save_health_record(record_data)
        return {
            "success": success,
            "message": message,
            "record_id": record_id,
            "timestamp": get_current_datetime()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error saving record: {str(e)}",
            "record_id": None,
            "timestamp": get_current_datetime()
        }


def get_animal_history(animal_id, limit=20):
    """
    TOOL: Get the health history for a specific animal.
    
    This tool is used by the Monitoring Agent to compare current
    health data with previous records. It helps identify trends
    like weight loss, temperature changes, or recurring symptoms.
    
    Args:
        animal_id (str): The animal's unique ID
        limit (int): Maximum number of records to retrieve
    
    Returns:
        dict: Result with history records
    """
    try:
        records = db.get_animal_history(animal_id, limit)
        return {
            "success": True,
            "animal_id": animal_id,
            "record_count": len(records),
            "records": records,
            "message": f"Found {len(records)} health records for {animal_id}."
        }
    except Exception as e:
        return {
            "success": False,
            "animal_id": animal_id,
            "record_count": 0,
            "records": [],
            "message": f"❌ Error retrieving history: {str(e)}"
        }


def get_all_animal_ids():
    """
    TOOL: Get a list of all registered animal IDs.
    
    Used by the dashboard to show which animals are in the system.
    
    Returns:
        list: List of animal ID strings
    """
    try:
        stats = db.get_dashboard_stats()
        return stats.get("animal_ids", [])
    except Exception as e:
        print(f"Error getting animal IDs: {e}")
        return []


def get_dashboard_data():
    """
    TOOL: Get statistics for the dashboard.
    
    This tool provides summary data for the main dashboard view,
    including total animals, health status breakdown, and recent records.
    
    Returns:
        dict: Dashboard statistics
    """
    try:
        return db.get_dashboard_stats()
    except Exception as e:
        return {
            "total_animals": 0,
            "total_records": 0,
            "status_counts": {"Healthy": 0, "Needs Monitoring": 0, 
                            "Warning": 0, "Critical": 0, "Unknown": 0},
            "recent_records": [],
            "animal_ids": [],
        }


def search_animals(search_term):
    """
    TOOL: Search for animals by ID, type, or breed.
    
    Args:
        search_term (str): Text to search for
    
    Returns:
        list: Matching animal records
    """
    try:
        return db.search_animals(search_term)
    except Exception as e:
        print(f"Error searching: {e}")
        return []
