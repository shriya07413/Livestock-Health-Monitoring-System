"""
Nutrition Agent
================
This agent provides feeding and nutrition guidance for livestock.

WHAT DOES THIS AGENT DO?
- Provides general nutrition recommendations based on animal type, age, and condition
- Adjusts advice based on current health status
- Uses domain knowledge about livestock nutrition
- Calls the LLM for personalized recommendations

SAFETY NOTE:
This agent provides GENERAL nutrition information only.
It does NOT prescribe medication or specific medical treatments.
"""

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from utils.config import get_api_key, is_demo_mode, APP_CONFIG
from tools.health_tools import get_health_knowledge


class NutritionAgent:
    """
    Nutrition Agent - Provides feeding and nutrition guidance for livestock.
    """
    
    def __init__(self):
        """Initialize the Nutrition Agent."""
        self.name = "Nutrition Agent"
        self.role = (
            "You are a livestock nutrition advisor. You provide general feeding "
            "and nutrition guidance based on the animal's type, age, weight, "
            "and current health status. You give safe, general recommendations. "
            "You do NOT prescribe medication or specific medical treatments. "
            "Always recommend consulting a veterinarian or animal nutritionist "
            "for specific dietary plans."
        )
    
    def get_advice(self, animal_data, health_status="Unknown"):
        """
        Generate nutrition advice for the given animal.
        
        Args:
            animal_data (dict): Animal information
            health_status (str): Current health status from Health Agent
        
        Returns:
            dict: Nutrition advice and recommendations
        """
        # ─── Use knowledge retrieval tool ───
        knowledge = get_health_knowledge(
            animal_type=animal_data.get("animal_type", "Unknown"),
            topic="feeding"
        )
        
        # ─── Get AI-powered nutrition advice or demo response ───
        if is_demo_mode():
            advice = self._get_demo_advice(animal_data, health_status, knowledge)
        else:
            advice = self._get_ai_advice(animal_data, health_status, knowledge)
        
        return {
            "agent": self.name,
            "nutrition_advice": advice,
            "animal_type": animal_data.get("animal_type", "Unknown"),
            "health_status": health_status,
        }
    
    def _get_ai_advice(self, animal_data, health_status, knowledge):
        """Get AI-powered nutrition advice from OpenAI."""
        try:
            client = OpenAI(api_key=get_api_key())
            
            prompt = f"""Provide general nutrition and feeding guidance for this livestock animal.

ANIMAL INFORMATION:
- Type: {animal_data.get('animal_type', 'Unknown')}
- Breed: {animal_data.get('breed', 'Unknown')}
- Age: {animal_data.get('age', 'Unknown')}
- Gender: {animal_data.get('gender', 'Unknown')}
- Weight: {animal_data.get('weight', 'N/A')} kg
- Current Health Status: {health_status}
- Current Food Intake: {animal_data.get('food_intake', 'Normal')}
- Current Water Intake: {animal_data.get('water_intake', 'Normal')}
- Symptoms: {animal_data.get('symptoms', 'None')}

FEEDING KNOWLEDGE: {knowledge.get('information', 'N/A')}

Provide advice in these categories:
1. DAILY FEEDING RECOMMENDATIONS: General feeding guidelines
2. WATER REQUIREMENTS: Hydration needs
3. NUTRITIONAL SUPPLEMENTS: General supplement suggestions if applicable
4. DIETARY ADJUSTMENTS: Any changes needed based on current health
5. FEEDING TIPS: Practical feeding advice

Keep advice general and safe. Do NOT prescribe medications.
Recommend consulting a vet or animal nutritionist for specific plans."""

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
            return self._get_demo_advice(animal_data, health_status, knowledge)
    
    def _get_demo_advice(self, animal_data, health_status, knowledge):
        """Generate demo nutrition advice."""
        animal_type = animal_data.get("animal_type", "Animal").lower()
        weight = animal_data.get("weight", 0)
        
        advice_lines = []
        advice_lines.append(f"🍽️ **NUTRITION RECOMMENDATIONS** (Demo Mode)")
        advice_lines.append(f"")
        advice_lines.append(f"**Animal:** {animal_data.get('animal_type', 'Unknown')} "
                          f"({animal_data.get('breed', 'Unknown breed')})")
        advice_lines.append(f"")
        
        # General feeding recommendation
        advice_lines.append(f"**1. DAILY FEEDING:**")
        try:
            w = float(weight)
            if w > 0:
                dry_matter = round(w * 0.025, 1)  # ~2.5% of body weight
                advice_lines.append(f"  • Estimated dry matter intake: ~{dry_matter} kg/day")
                advice_lines.append(f"  • Based on {w} kg body weight (2.5% guideline)")
        except (ValueError, TypeError):
            pass
        
        if animal_type in ("cow", "buffalo"):
            advice_lines.append(f"  • Provide good quality roughage (hay, silage, green fodder)")
            advice_lines.append(f"  • Supplement with concentrates as needed")
            advice_lines.append(f"  • Ensure adequate mineral and vitamin supplementation")
        elif animal_type in ("goat", "sheep"):
            advice_lines.append(f"  • Provide a variety of browse, hay, and pasture")
            advice_lines.append(f"  • Small amounts of grain/concentrates may be beneficial")
            advice_lines.append(f"  • Mineral licks should be available")
        else:
            advice_lines.append(f"  • Provide species-appropriate feed")
            advice_lines.append(f"  • Ensure balanced nutrition")
        
        advice_lines.append(f"")
        advice_lines.append(f"**2. WATER REQUIREMENTS:**")
        advice_lines.append(f"  • Fresh, clean water should be available at all times")
        if animal_type in ("cow", "buffalo"):
            advice_lines.append(f"  • Adult cattle typically need 40-80 liters of water daily")
        elif animal_type in ("goat", "sheep"):
            advice_lines.append(f"  • Adult goats/sheep typically need 4-12 liters daily")
        
        advice_lines.append(f"")
        advice_lines.append(f"**3. HEALTH-BASED ADJUSTMENTS:**")
        if health_status in ("Warning", "Critical"):
            advice_lines.append(f"  ⚠️ Given the current health status ({health_status}):")
            advice_lines.append(f"  • Ensure easy access to food and water")
            advice_lines.append(f"  • Consider offering more palatable feeds to encourage eating")
            advice_lines.append(f"  • Consult a veterinarian about specific dietary needs")
        elif health_status == "Needs Monitoring":
            advice_lines.append(f"  • Monitor food and water intake closely")
            advice_lines.append(f"  • Maintain current feeding routine")
        else:
            advice_lines.append(f"  • Continue with regular feeding schedule")
        
        if knowledge.get("found"):
            advice_lines.append(f"")
            advice_lines.append(f"**4. REFERENCE INFORMATION:**")
            advice_lines.append(f"  {knowledge['information']}")
        
        advice_lines.append(f"")
        advice_lines.append(f"---")
        advice_lines.append(f"*Consult a veterinarian or animal nutritionist for a specific diet plan.*")
        advice_lines.append(f"*[Demo Mode: Connect an OpenAI API key for personalized advice]*")
        
        return "\n".join(advice_lines)
