"""
Monitoring Agent
==================
This agent tracks animal health over time and identifies changes.

WHAT DOES THIS AGENT DO?
- Retrieves previous health records from the database (memory)
- Compares current data with historical data
- Identifies trends (improving, declining, stable)
- Flags significant changes that need attention

AGENTIC AI CONCEPTS:
- Agent Memory: Uses database to remember past interactions
- Agent State: Tracks the health state of animals over time
- Tool Usage: Uses get_animal_history tool to retrieve records
"""

from tools.database_tools import get_animal_history
from utils.helpers import get_current_datetime


class MonitoringAgent:
    """
    Monitoring Agent - Tracks animal health over time and identifies changes.
    
    This agent demonstrates the concept of "agent memory" by using
    the database to remember and compare past health records.
    """
    
    def __init__(self):
        """Initialize the Monitoring Agent."""
        self.name = "Monitoring Agent"
        self.role = (
            "You track livestock health over time. You compare current "
            "health data with previous records to identify trends, "
            "changes, and potential concerns."
        )
    
    def monitor(self, animal_id, current_data):
        """
        Monitor an animal by comparing current data with history.
        
        WORKFLOW:
        1. Use get_animal_history TOOL to retrieve past records
        2. Compare current metrics with previous values
        3. Identify trends and changes
        4. Return monitoring assessment
        
        Args:
            animal_id (str): The animal's unique ID
            current_data (dict): Current health data
        
        Returns:
            dict: Monitoring results with trends and comparisons
        """
        # ─── STEP 1: Use database tool to get history (Agent Memory) ───
        history_result = get_animal_history(animal_id)
        history = history_result.get("records", [])
        
        # ─── STEP 2: Analyze changes ───
        comparisons = []
        trends = []
        overall_trend = "New Record"
        
        if len(history) > 0:
            # Get the most recent previous record
            previous = history[0]  # Most recent record
            
            # Compare temperature
            temp_comparison = self._compare_metric(
                current=current_data.get("temperature", 0),
                previous=previous.get("temperature", 0),
                metric_name="Temperature",
                unit="°C",
                lower_is_better_threshold=0.5  # Significant if change > 0.5°C
            )
            comparisons.append(temp_comparison)
            
            # Compare weight
            weight_comparison = self._compare_metric(
                current=current_data.get("weight", 0),
                previous=previous.get("weight", 0),
                metric_name="Weight",
                unit="kg",
                lower_is_better_threshold=5  # Significant if change > 5kg
            )
            comparisons.append(weight_comparison)
            
            # Compare health status
            current_status = current_data.get("health_status", "Unknown")
            previous_status = previous.get("health_status", "Unknown")
            
            status_order = {"Healthy": 0, "Normal": 0, "Needs Monitoring": 1, 
                          "Warning": 2, "Critical": 3, "Unknown": -1}
            
            current_level = status_order.get(current_status, -1)
            previous_level = status_order.get(previous_status, -1)
            
            if current_level < previous_level and previous_level >= 0:
                trends.append("📈 Health status has IMPROVED")
                overall_trend = "Improving"
            elif current_level > previous_level and current_level >= 0:
                trends.append("📉 Health status has DECLINED")
                overall_trend = "Declining"
            elif current_level == previous_level and current_level >= 0:
                trends.append("➡️ Health status is STABLE")
                overall_trend = "Stable"
            
            # Check for recurring symptoms
            current_symptoms = current_data.get("symptoms", "").lower()
            previous_symptoms = previous.get("symptoms", "").lower()
            
            if current_symptoms and previous_symptoms:
                # Simple check for overlapping symptom keywords
                current_words = set(current_symptoms.split())
                previous_words = set(previous_symptoms.split())
                common = current_words & previous_words
                
                # Filter out common words
                stop_words = {"and", "the", "a", "is", "in", "of", "not", "no", "with"}
                meaningful_common = common - stop_words
                
                if meaningful_common and len(meaningful_common) >= 1:
                    trends.append(f"🔄 Some symptoms appear to be recurring")
            
            # Compare food/water intake
            if (current_data.get("food_intake", "").lower() in 
                ("reduced", "very low", "none") and
                previous.get("food_intake", "").lower() in 
                ("reduced", "very low", "none")):
                trends.append("⚠️ Reduced food intake persists from previous check")
            
            if (current_data.get("activity_level", "").lower() in 
                ("reduced", "very low") and
                previous.get("activity_level", "").lower() in 
                ("reduced", "very low")):
                trends.append("⚠️ Reduced activity persists from previous check")
        
        else:
            trends.append("📝 This is the first health record for this animal")
            overall_trend = "First Record"
        
        # ─── STEP 3: Build monitoring summary ───
        monitoring_text = self._build_monitoring_summary(
            animal_id, current_data, history, comparisons, trends, overall_trend
        )
        
        return {
            "agent": self.name,
            "animal_id": animal_id,
            "monitoring_notes": monitoring_text,
            "overall_trend": overall_trend,
            "comparisons": comparisons,
            "trends": trends,
            "history_count": len(history),
            "assessed_at": get_current_datetime(),
        }
    
    def _compare_metric(self, current, previous, metric_name, unit, 
                        lower_is_better_threshold=1.0):
        """
        Compare a current metric value with a previous one.
        
        Args:
            current: Current value
            previous: Previous value
            metric_name: Name of the metric
            unit: Unit of measurement
            lower_is_better_threshold: Threshold for significant change
        
        Returns:
            dict: Comparison result
        """
        try:
            curr_val = float(current)
            prev_val = float(previous)
            
            if prev_val == 0:
                return {
                    "metric": metric_name,
                    "current": curr_val,
                    "previous": prev_val,
                    "change": "N/A",
                    "direction": "unknown",
                    "significant": False,
                    "message": f"{metric_name}: No previous value for comparison"
                }
            
            change = curr_val - prev_val
            pct_change = (change / prev_val) * 100 if prev_val != 0 else 0
            
            if abs(change) < lower_is_better_threshold:
                direction = "stable"
                emoji = "➡️"
            elif change > 0:
                direction = "increased"
                emoji = "📈"
            else:
                direction = "decreased"
                emoji = "📉"
            
            return {
                "metric": metric_name,
                "current": curr_val,
                "previous": prev_val,
                "change": round(change, 2),
                "percent_change": round(pct_change, 1),
                "direction": direction,
                "significant": abs(change) >= lower_is_better_threshold,
                "message": (
                    f"{emoji} {metric_name}: {curr_val}{unit} "
                    f"(was {prev_val}{unit}, change: {change:+.1f}{unit})"
                )
            }
        except (ValueError, TypeError):
            return {
                "metric": metric_name,
                "current": current,
                "previous": previous,
                "change": "N/A",
                "direction": "unknown",
                "significant": False,
                "message": f"{metric_name}: Could not compare values"
            }
    
    def _build_monitoring_summary(self, animal_id, current_data, history,
                                   comparisons, trends, overall_trend):
        """Build a formatted monitoring summary text."""
        lines = []
        lines.append(f"📊 **MONITORING REPORT** for {animal_id}")
        lines.append(f"")
        lines.append(f"**Overall Trend:** {overall_trend}")
        lines.append(f"**Previous Records:** {len(history)}")
        lines.append(f"")
        
        if comparisons:
            lines.append(f"**Metric Comparisons:**")
            for comp in comparisons:
                if comp.get("significant"):
                    lines.append(f"  ⚡ {comp['message']}")
                else:
                    lines.append(f"  {comp['message']}")
            lines.append(f"")
        
        if trends:
            lines.append(f"**Trends & Observations:**")
            for trend in trends:
                lines.append(f"  {trend}")
            lines.append(f"")
        
        # Add recommendations based on trends
        lines.append(f"**Monitoring Recommendations:**")
        if overall_trend == "Declining":
            lines.append(f"  🔴 Health appears to be declining. Increased monitoring recommended.")
            lines.append(f"  🔴 Consider scheduling a veterinary consultation.")
        elif overall_trend == "Improving":
            lines.append(f"  🟢 Health appears to be improving. Continue current care.")
        elif overall_trend == "Stable":
            lines.append(f"  🟡 Health is stable. Maintain regular monitoring schedule.")
        else:
            lines.append(f"  📝 Baseline record established. Future checks will be compared to this.")
        
        return "\n".join(lines)
