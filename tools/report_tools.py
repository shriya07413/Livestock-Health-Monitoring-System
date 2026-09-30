"""
Report Tools for AI Agents
=============================
These tools help generate reports and charts for livestock health monitoring.
"""

import os
from datetime import datetime
from utils.helpers import get_current_datetime, format_health_status
from utils.config import APP_CONFIG

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
except ImportError:
    matplotlib = None
    plt = None
    mdates = None


def generate_health_report(animal_data, health_analysis, nutrition_advice,
                           monitoring_notes, history=None):
    """
    TOOL: Generate a formatted health monitoring report.
    
    The Report Agent uses this tool to create a comprehensive
    report combining information from all specialist agents.
    
    Args:
        animal_data (dict): Animal information
        health_analysis (str): Analysis from Health Agent
        nutrition_advice (str): Advice from Nutrition Agent
        monitoring_notes (str): Notes from Monitoring Agent
        history (list): Previous health records (optional)
    
    Returns:
        dict: Report content and metadata
    """
    report_date = get_current_datetime()
    
    # Build the report
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("🐄 LIVESTOCK HEALTH MONITORING REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"📅 Report Date: {report_date}")
    report_lines.append("")
    
    # --- Animal Information Section ---
    report_lines.append("─" * 40)
    report_lines.append("📋 ANIMAL INFORMATION")
    report_lines.append("─" * 40)
    report_lines.append(f"  Animal ID:    {animal_data.get('animal_id', 'N/A')}")
    report_lines.append(f"  Type:         {animal_data.get('animal_type', 'N/A')}")
    report_lines.append(f"  Breed:        {animal_data.get('breed', 'N/A')}")
    report_lines.append(f"  Age:          {animal_data.get('age', 'N/A')}")
    report_lines.append(f"  Gender:       {animal_data.get('gender', 'N/A')}")
    report_lines.append(f"  Weight:       {animal_data.get('weight', 'N/A')} kg")
    report_lines.append(f"  Temperature:  {animal_data.get('temperature', 'N/A')}°C")
    report_lines.append("")
    
    # --- Current Observations ---
    report_lines.append("─" * 40)
    report_lines.append("🔍 CURRENT OBSERVATIONS")
    report_lines.append("─" * 40)
    report_lines.append(f"  Symptoms:       {animal_data.get('symptoms', 'None reported')}")
    report_lines.append(f"  Food Intake:    {animal_data.get('food_intake', 'N/A')}")
    report_lines.append(f"  Water Intake:   {animal_data.get('water_intake', 'N/A')}")
    report_lines.append(f"  Activity Level: {animal_data.get('activity_level', 'N/A')}")
    report_lines.append(f"  Health Status:  {format_health_status(animal_data.get('health_status', 'unknown'))}")
    report_lines.append("")
    
    # --- Health Analysis ---
    report_lines.append("─" * 40)
    report_lines.append("🏥 HEALTH ANALYSIS")
    report_lines.append("─" * 40)
    report_lines.append(health_analysis if health_analysis else "  No analysis available.")
    report_lines.append("")
    
    # --- Nutrition Advice ---
    report_lines.append("─" * 40)
    report_lines.append("🍽️ NUTRITION RECOMMENDATIONS")
    report_lines.append("─" * 40)
    report_lines.append(nutrition_advice if nutrition_advice else "  No nutrition advice available.")
    report_lines.append("")
    
    # --- Monitoring Notes ---
    report_lines.append("─" * 40)
    report_lines.append("📊 MONITORING NOTES")
    report_lines.append("─" * 40)
    report_lines.append(monitoring_notes if monitoring_notes else "  No previous records for comparison.")
    report_lines.append("")
    
    # --- Previous Records Summary ---
    if history and len(history) > 1:
        report_lines.append("─" * 40)
        report_lines.append("📜 HEALTH HISTORY SUMMARY")
        report_lines.append("─" * 40)
        report_lines.append(f"  Total previous records: {len(history) - 1}")
        for i, record in enumerate(history[1:4], 1):  # Show last 3 previous
            report_lines.append(f"  Record {i}: {record.get('created_at', 'N/A')} - "
                              f"Status: {record.get('health_status', 'N/A')}, "
                              f"Temp: {record.get('temperature', 'N/A')}°C")
        report_lines.append("")
    
    # --- Disclaimer ---
    report_lines.append("─" * 40)
    report_lines.append("⚠️ DISCLAIMER")
    report_lines.append("─" * 40)
    report_lines.append(APP_CONFIG["safety_disclaimer"])
    report_lines.append("")
    report_lines.append("=" * 60)
    report_lines.append("End of Report")
    report_lines.append("=" * 60)
    
    report_text = "\n".join(report_lines)
    
    # Try to save the report to a file
    report_filename = None
    try:
        reports_dir = APP_CONFIG["reports_dir"]
        os.makedirs(reports_dir, exist_ok=True)
        
        animal_id = animal_data.get("animal_id", "UNKNOWN")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = os.path.join(reports_dir, f"report_{animal_id}_{timestamp}.txt")
        
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report_text)
    except Exception as e:
        print(f"Warning: Could not save report file: {e}")
    
    return {
        "report_text": report_text,
        "report_file": report_filename,
        "generated_at": report_date,
        "animal_id": animal_data.get("animal_id", "N/A")
    }


def create_health_chart(animal_id, history_records, chart_type="temperature"):
    """
    TOOL: Create a health trend chart using Matplotlib.
    
    This tool generates visual charts showing how an animal's
    health metrics have changed over time.
    
    Args:
        animal_id (str): Animal's unique ID
        history_records (list): List of health record dictionaries
        chart_type (str): Type of chart - "temperature", "weight", or "combined"
    
    Returns:
        dict: Chart file path and metadata
    """
    if not history_records or len(history_records) == 0:
        return {
            "success": False,
            "message": f"No health records found for {animal_id}.",
            "chart_path": None
        }
    
    try:
        charts_dir = APP_CONFIG["charts_dir"]
        os.makedirs(charts_dir, exist_ok=True)
        
        # Parse dates and values from records
        dates = []
        temperatures = []
        weights = []
        statuses = []
        
        # Process records (they come newest first, so reverse for chronological order)
        for record in reversed(history_records):
            try:
                date_str = record.get("created_at", "")
                if date_str:
                    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    dates.append(date)
                    temperatures.append(float(record.get("temperature", 0)))
                    weights.append(float(record.get("weight", 0)))
                    statuses.append(record.get("health_status", "Unknown"))
            except (ValueError, TypeError):
                continue
        
        if len(dates) == 0:
            return {
                "success": False,
                "message": "Could not parse any valid records for charting.",
                "chart_path": None
            }
        
        # Set the visual style
        plt.style.use('seaborn-v0_8-whitegrid')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if chart_type == "combined" and len(dates) > 0:
            # Create a figure with 2 subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            fig.suptitle(f'🐄 Health Trends for {animal_id}', 
                        fontsize=14, fontweight='bold')
            
            # Temperature chart
            ax1.plot(dates, temperatures, 'r-o', label='Temperature (°C)', 
                    linewidth=2, markersize=6)
            
            # Add normal range shading for temperature
            animal_type = history_records[0].get("animal_type", "").lower()
            from utils.config import get_temp_range
            temp_min, temp_max = get_temp_range(animal_type)
            ax1.axhspan(temp_min, temp_max, alpha=0.15, color='green', 
                       label=f'Normal Range ({temp_min}-{temp_max}°C)')
            
            ax1.set_ylabel('Temperature (°C)')
            ax1.set_title('Temperature Over Time')
            ax1.legend(loc='upper right', fontsize=8)
            ax1.grid(True, alpha=0.3)
            
            # Weight chart
            valid_weights = [(d, w) for d, w in zip(dates, weights) if w > 0]
            if valid_weights:
                w_dates, w_vals = zip(*valid_weights)
                ax2.plot(w_dates, w_vals, 'b-s', label='Weight (kg)', 
                        linewidth=2, markersize=6)
            
            ax2.set_ylabel('Weight (kg)')
            ax2.set_title('Weight Over Time')
            ax2.set_xlabel('Date')
            ax2.legend(loc='upper right', fontsize=8)
            ax2.grid(True, alpha=0.3)
            
            # Format dates on x-axis
            for ax in [ax1, ax2]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            chart_path = os.path.join(charts_dir, 
                                       f"combined_{animal_id}_{timestamp}.png")
            
        elif chart_type == "temperature":
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(dates, temperatures, 'r-o', linewidth=2, markersize=6,
                   label='Temperature (°C)')
            
            animal_type = history_records[0].get("animal_type", "").lower()
            from utils.config import get_temp_range
            temp_min, temp_max = get_temp_range(animal_type)
            ax.axhspan(temp_min, temp_max, alpha=0.15, color='green',
                      label=f'Normal Range ({temp_min}-{temp_max}°C)')
            
            ax.set_title(f'🌡️ Temperature History - {animal_id}', fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Temperature (°C)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            chart_path = os.path.join(charts_dir, 
                                       f"temp_{animal_id}_{timestamp}.png")
            
        elif chart_type == "weight":
            fig, ax = plt.subplots(figsize=(10, 5))
            valid_weights = [(d, w) for d, w in zip(dates, weights) if w > 0]
            
            if valid_weights:
                w_dates, w_vals = zip(*valid_weights)
                ax.plot(w_dates, w_vals, 'b-s', linewidth=2, markersize=6,
                       label='Weight (kg)')
            
            ax.set_title(f'⚖️ Weight History - {animal_id}', fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Weight (kg)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            chart_path = os.path.join(charts_dir, 
                                       f"weight_{animal_id}_{timestamp}.png")
        else:
            return {
                "success": False,
                "message": f"Unknown chart type: {chart_type}",
                "chart_path": None
            }
        
        plt.tight_layout()
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        return {
            "success": True,
            "message": f"Chart saved successfully.",
            "chart_path": chart_path,
            "chart_type": chart_type,
            "data_points": len(dates)
        }
        
    except Exception as e:
        plt.close('all')
        return {
            "success": False,
            "message": f"Error creating chart: {str(e)}",
            "chart_path": None
        }


def get_current_date():
    """
    TOOL: Get the current date and time.
    
    Simple utility tool that agents can call to get the current timestamp.
    
    Returns:
        str: Current date and time
    """
    return get_current_datetime()
