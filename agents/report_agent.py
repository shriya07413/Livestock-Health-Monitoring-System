"""
Report Agent
==============
This agent generates comprehensive health monitoring reports.

WHAT DOES THIS AGENT DO?
- Collects results from all other agents
- Generates a formatted, professional report
- Uses the report generation tool
- Optionally saves the report to a file
"""

from tools.report_tools import generate_health_report, get_current_date
from tools.database_tools import get_animal_history


class ReportAgent:
    """
    Report Agent - Generates comprehensive health monitoring reports.
    
    This agent takes the outputs from all other agents and combines
    them into a single, well-formatted report.
    """
    
    def __init__(self):
        """Initialize the Report Agent."""
        self.name = "Report Agent"
        self.role = (
            "You compile health monitoring reports by combining information "
            "from other agents into clear, structured documents."
        )
    
    def generate(self, animal_data, health_result, nutrition_result, 
                 monitoring_result):
        """
        Generate a comprehensive health monitoring report.
        
        WORKFLOW:
        1. Collect results from Health, Nutrition, and Monitoring agents
        2. Get history records using the database tool
        3. Use the generate_health_report TOOL to create the report
        4. Return the formatted report
        
        Args:
            animal_data (dict): Basic animal information
            health_result (dict): Results from Health Analysis Agent
            nutrition_result (dict): Results from Nutrition Agent
            monitoring_result (dict): Results from Monitoring Agent
        
        Returns:
            dict: Report content and metadata
        """
        # ─── Collect data from each agent's results ───
        
        # Add health status to animal_data for the report
        animal_data_with_status = {**animal_data}
        animal_data_with_status["health_status"] = health_result.get(
            "health_status", "Unknown"
        )
        
        # Get health analysis text
        health_analysis = health_result.get("ai_analysis", "No analysis available.")
        
        # Get nutrition advice text
        nutrition_advice = nutrition_result.get("nutrition_advice", "No advice available.")
        
        # Get monitoring notes
        monitoring_notes = monitoring_result.get("monitoring_notes", "No monitoring data.")
        
        # ─── Get history using database tool ───
        history_result = get_animal_history(
            animal_data.get("animal_id", "UNKNOWN")
        )
        history = history_result.get("records", [])
        
        # ─── Use the report generation tool ───
        report = generate_health_report(
            animal_data=animal_data_with_status,
            health_analysis=health_analysis,
            nutrition_advice=nutrition_advice,
            monitoring_notes=monitoring_notes,
            history=history
        )
        
        return {
            "agent": self.name,
            "report_text": report.get("report_text", ""),
            "report_file": report.get("report_file", None),
            "generated_at": report.get("generated_at", get_current_date()),
            "animal_id": animal_data.get("animal_id", "N/A"),
        }
