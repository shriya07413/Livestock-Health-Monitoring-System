"""
Health Analysis Agent
======================
This agent is responsible for analyzing animal health data.

WHAT DOES THIS AGENT DO?
- Takes animal information (symptoms, temperature, weight, etc.)
- Uses tools to calculate health metrics
- Calls the OpenAI API for intelligent analysis
- Returns a structured health assessment

AGENTIC AI CONCEPTS DEMONSTRATED:
- Specialized agent with a specific role
- Tool usage (calculate_health_metrics)
- LLM integration for reasoning
- Structured output
"""

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from utils.config import get_api_key, is_demo_mode, APP_CONFIG
from tools.health_tools import calculate_health_metrics, get_health_knowledge


class HealthAgent:
    """
    Health Analysis Agent - Analyzes animal health data and provides assessments.
    
    This agent combines rule-based health metric calculations with
    AI-powered analysis to provide comprehensive health assessments.
    """
    
    def __init__(self):
        """Initialize the Health Analysis Agent."""
        self.name = "Health Analysis Agent"
        self.role = (
            "You are a livestock health analysis assistant. You analyze animal "
            "health data including symptoms, vital signs, and behavioral changes "
            "to provide educational health assessments. You are NOT a veterinarian. "
            "Always recommend consulting a qualified veterinarian for proper diagnosis."
        )
    
    def analyze(self, animal_data):
        """
        Analyze animal health data and return a structured assessment.
        
        This is the main function of the Health Agent. Here's what happens:
        1. First, it uses the calculate_health_metrics TOOL to get baseline metrics
        2. Then, it uses the get_health_knowledge TOOL for domain knowledge
        3. Finally, it calls the LLM API for intelligent analysis
        4. Returns everything in a structured format
        
        Args:
            animal_data (dict): Dictionary containing:
                - animal_type, breed, age, gender
                - weight, temperature
                - symptoms, food_intake, water_intake, activity_level
        
        Returns:
            dict: Health analysis results
        """
        # ─── STEP 1: Use the health metrics tool ───
        metrics = calculate_health_metrics(
            animal_type=animal_data.get("animal_type", "Unknown"),
            weight=animal_data.get("weight", 0),
            temperature=animal_data.get("temperature", 0),
            symptoms_text=animal_data.get("symptoms", ""),
            food_intake=animal_data.get("food_intake", "Normal"),
            water_intake=animal_data.get("water_intake", "Normal"),
            activity_level=animal_data.get("activity_level", "Normal"),
        )
        
        # ─── STEP 2: Use the knowledge retrieval tool ───
        knowledge = get_health_knowledge(
            animal_type=animal_data.get("animal_type", "Unknown"),
            topic="general"
        )
        
        # ─── STEP 3: Get AI-powered analysis ───
        if is_demo_mode():
            ai_analysis = self._get_demo_analysis(animal_data, metrics)
        else:
            ai_analysis = self._get_ai_analysis(animal_data, metrics, knowledge)
        
        # ─── STEP 4: Combine everything into a structured result ───
        result = {
            "agent": self.name,
            "health_status": metrics["health_status"],
            "status_emoji": metrics["status_emoji"],
            "risk_score": metrics["risk_score"],
            "temperature_status": metrics["temperature_status"],
            "weight_status": metrics["weight_status"],
            "normal_temp_range": metrics["normal_temp_range"],
            "normal_weight_range": metrics["normal_weight_range"],
            "warnings": metrics["warnings"],
            "warning_count": metrics["warning_count"],
            "symptom_count": metrics["symptom_count"],
            "symptoms_list": metrics["symptoms_list"],
            "ai_analysis": ai_analysis,
            "assessed_at": metrics["assessed_at"],
            "disclaimer": APP_CONFIG["safety_disclaimer"],
        }
        
        return result
    
    def _get_ai_analysis(self, animal_data, metrics, knowledge):
        """
        Get AI-powered health analysis from OpenAI API.
        
        HOW THE API CALL WORKS:
        1. We create a prompt with the animal's data and metrics
        2. We send it to the OpenAI API
        3. The API returns an intelligent analysis
        4. We return the analysis text
        
        Args:
            animal_data (dict): Animal information
            metrics (dict): Calculated health metrics
            knowledge (dict): Domain knowledge
        
        Returns:
            str: AI-generated health analysis
        """
        try:
            client = OpenAI(api_key=get_api_key())
            
            # Build the prompt for the AI
            prompt = f"""Analyze the following livestock health data and provide a structured assessment.

ANIMAL INFORMATION:
- Type: {animal_data.get('animal_type', 'Unknown')}
- Breed: {animal_data.get('breed', 'Unknown')}
- Age: {animal_data.get('age', 'Unknown')}
- Gender: {animal_data.get('gender', 'Unknown')}
- Weight: {animal_data.get('weight', 'N/A')} kg
- Temperature: {animal_data.get('temperature', 'N/A')}°C

SYMPTOMS: {animal_data.get('symptoms', 'None reported')}
FOOD INTAKE: {animal_data.get('food_intake', 'Normal')}
WATER INTAKE: {animal_data.get('water_intake', 'Normal')}
ACTIVITY LEVEL: {animal_data.get('activity_level', 'Normal')}

CALCULATED METRICS:
- Health Status: {metrics['health_status']}
- Risk Score: {metrics['risk_score']}
- Temperature Status: {metrics['temperature_status']}
- Weight Status: {metrics['weight_status']}
- Normal Temperature Range: {metrics['normal_temp_range']}

DOMAIN KNOWLEDGE: {knowledge.get('information', 'N/A')}

Provide your analysis in the following format:
1. SUMMARY: Brief overview of the animal's health
2. KEY CONCERNS: List any health concerns
3. POSSIBLE CONDITIONS: What conditions might these symptoms suggest (educational only)
4. RECOMMENDED ACTIONS: What steps should be taken
5. URGENCY LEVEL: How urgently should a vet be consulted

Remember: This is for educational monitoring only. Always recommend veterinary consultation."""

            response = client.chat.completions.create(
                model=APP_CONFIG["model"],
                messages=[
                    {"role": "system", "content": self.role},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=APP_CONFIG["max_tokens"],
                temperature=APP_CONFIG["temperature"],
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return (
                f"⚠️ AI analysis temporarily unavailable: {str(e)}\n\n"
                f"Based on calculated metrics:\n"
                f"• Health Status: {metrics['health_status']}\n"
                f"• Risk Score: {metrics['risk_score']}/10\n"
                f"• Temperature: {metrics['temperature_status']}\n"
                f"• Weight: {metrics['weight_status']}\n"
                + ("\n⚠️ Warnings:\n" + "\n".join(f"  • {w}" for w in metrics['warnings']) 
                   if metrics['warnings'] else "")
            )
    
    def _get_demo_analysis(self, animal_data, metrics):
        """
        Generate a demo analysis when no API key is available.
        
        This allows the application to work in demo mode.
        
        Args:
            animal_data (dict): Animal information
            metrics (dict): Calculated health metrics
        
        Returns:
            str: Demo health analysis text
        """
        analysis_lines = []
        analysis_lines.append(f"📋 **HEALTH ANALYSIS REPORT** (Demo Mode)")
        analysis_lines.append(f"")
        analysis_lines.append(f"**1. SUMMARY:**")
        analysis_lines.append(f"The {animal_data.get('animal_type', 'animal')} "
                            f"({animal_data.get('breed', 'Unknown breed')}, "
                            f"Age: {animal_data.get('age', 'Unknown')}) has been assessed.")
        analysis_lines.append(f"Overall health status: **{metrics['health_status']}** "
                            f"{metrics['status_emoji']}")
        analysis_lines.append(f"Risk Score: {metrics['risk_score']}/10")
        analysis_lines.append(f"")
        
        analysis_lines.append(f"**2. KEY CONCERNS:**")
        if metrics['warnings']:
            for warning in metrics['warnings']:
                analysis_lines.append(f"  • {warning}")
        else:
            analysis_lines.append(f"  • No significant concerns identified.")
        analysis_lines.append(f"")
        
        analysis_lines.append(f"**3. VITAL SIGNS:**")
        analysis_lines.append(f"  • Temperature: {animal_data.get('temperature', 'N/A')}°C "
                            f"({metrics['temperature_status']})")
        analysis_lines.append(f"  • Normal range: {metrics['normal_temp_range']}")
        analysis_lines.append(f"  • Weight: {animal_data.get('weight', 'N/A')} kg "
                            f"({metrics['weight_status']})")
        analysis_lines.append(f"")
        
        analysis_lines.append(f"**4. SYMPTOMS ASSESSMENT:**")
        if metrics['symptoms_list']:
            analysis_lines.append(f"  Reported {metrics['symptom_count']} symptom(s):")
            for symptom in metrics['symptoms_list']:
                analysis_lines.append(f"  • {symptom}")
        else:
            analysis_lines.append(f"  No symptoms reported.")
        analysis_lines.append(f"")
        
        analysis_lines.append(f"**5. RECOMMENDED ACTIONS:**")
        if metrics['health_status'] == "Critical":
            analysis_lines.append(f"  🚨 URGENT: Contact a veterinarian immediately.")
        elif metrics['health_status'] == "Warning":
            analysis_lines.append(f"  ⚠️ Schedule a veterinary consultation soon.")
            analysis_lines.append(f"  • Monitor vital signs closely.")
        elif metrics['health_status'] == "Needs Monitoring":
            analysis_lines.append(f"  🟡 Continue monitoring the animal.")
            analysis_lines.append(f"  • Record daily temperature and symptoms.")
            analysis_lines.append(f"  • Consult vet if symptoms persist.")
        else:
            analysis_lines.append(f"  🟢 Continue routine health monitoring.")
            analysis_lines.append(f"  • Maintain regular check-up schedule.")
        
        analysis_lines.append(f"")
        analysis_lines.append(f"---")
        analysis_lines.append(f"*[Demo Mode: Connect an OpenAI API key for AI-powered analysis]*")
        
        return "\n".join(analysis_lines)
