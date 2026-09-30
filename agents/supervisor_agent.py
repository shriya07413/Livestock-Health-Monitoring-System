"""
Supervisor / Manager Agent
==========================
The central orchestrator in our Multi-Agent Architecture.

WHAT DOES THE SUPERVISOR DO?
1. Receives the user's request (either from the Health Form or Conversational Chatbot).
2. Determines the required workflow and intent (Health Analysis, Nutrition Guidance, Historical Monitoring, Full Report, or General Q&A).
3. Dispatches tasks to Specialist Agents:
   - HealthAgent (Symptom analysis, risk calculation, vital checks)
   - NutritionAgent (Dietary recommendations, feeding adjustments)
   - MonitoringAgent (Historical comparisons, trend detection from SQLite memory)
   - ReportAgent (Consolidation into professional health reports)
4. Coordinates tool execution (database storage, retrieval, charting).
5. Aggregates responses from all specialists into a unified, coherent response.

AGENTIC AI CONCEPTS:
- Multi-Agent Orchestration (Supervisor Pattern / Central Coordinator)
- Workflow State Management (Agent State & Execution Graph)
- Tool Routing & Memory Access
"""

import json
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
from utils.config import get_api_key, is_demo_mode, APP_CONFIG
from agents.health_agent import HealthAgent
from agents.nutrition_agent import NutritionAgent
from agents.monitoring_agent import MonitoringAgent
from agents.report_agent import ReportAgent
from tools.database_tools import save_health_record, get_animal_history
from tools.health_tools import get_health_knowledge


class SupervisorAgent:
    """
    Coordinator Agent that manages the lifecycle of multi-agent tasks.
    """

    def __init__(self):
        self.name = "Supervisor Agent"
        self.role = (
            "You are the Chief Coordinator of the Livestock Health Monitoring System. "
            "You manage specialist agents (Health, Nutrition, Monitoring, Report), "
            "determine user intent, delegate tasks to the appropriate specialists, "
            "and synthesize comprehensive, helpful responses for livestock owners."
        )
        
        # Instantiate Specialist Sub-Agents
        self.health_agent = HealthAgent()
        self.nutrition_agent = NutritionAgent()
        self.monitoring_agent = MonitoringAgent()
        self.report_agent = ReportAgent()

    def process_health_intake(self, animal_data):
        """
        Execute the Complete Multi-Agent Workflow for an Animal Health Intake.
        
        Workflow Graph:
        User Input -> Supervisor -> [Health Agent + Monitoring Agent] -> Nutrition Agent -> Report Agent -> Save Memory -> Output
        
        Args:
            animal_data (dict): Collected livestock parameters
            
        Returns:
            dict: Structured workflow result containing all agent contributions
        """
        animal_id = animal_data.get("animal_id", "UNKNOWN")
        
        # 1. Step 1: Health Agent evaluates vitals & symptoms
        health_result = self.health_agent.analyze(animal_data)
        health_status = health_result.get("health_status", "Needs Monitoring")
        
        # 2. Step 2: Monitoring Agent compares with historical memory
        monitoring_result = self.monitoring_agent.monitor(animal_id, {
            **animal_data,
            "health_status": health_status
        })
        
        # 3. Step 3: Nutrition Agent prescribes dietary guidance based on status
        nutrition_result = self.nutrition_agent.get_advice(animal_data, health_status)
        
        # 4. Step 4: Report Agent compiles unified documentation
        report_result = self.report_agent.generate(
            animal_data=animal_data,
            health_result=health_result,
            nutrition_result=nutrition_result,
            monitoring_result=monitoring_result
        )
        
        # 5. Step 5: Save State & Results to SQLite Long-Term Memory
        record_to_save = {
            **animal_data,
            "health_status": health_status,
            "health_analysis": health_result.get("ai_analysis", ""),
            "nutrition_advice": nutrition_result.get("nutrition_advice", ""),
            "monitoring_notes": monitoring_result.get("monitoring_notes", ""),
        }
        db_save_result = save_health_record(record_to_save)
        
        # 6. Aggregate final state
        return {
            "supervisor": self.name,
            "animal_id": animal_id,
            "health_status": health_status,
            "status_emoji": health_result.get("status_emoji", "⚪"),
            "health_result": health_result,
            "monitoring_result": monitoring_result,
            "nutrition_result": nutrition_result,
            "report_result": report_result,
            "db_save_result": db_save_result,
            "disclaimer": APP_CONFIG["safety_disclaimer"]
        }

    def chat(self, user_message, chat_history=None):
        """
        Handle conversational Q&A by dynamically routing questions to the best specialist agent.
        
        Args:
            user_message (str): User query
            chat_history (list): Prior conversation turns [(user, bot), ...]
            
        Returns:
            str: AI Agent response
        """
        if chat_history is None:
            chat_history = []
            
        # Determine intent (Rule-based routing with LLM fallback)
        msg_lower = user_message.lower()
        
        if is_demo_mode():
            return self._demo_chat_response(user_message, msg_lower)
            
        return self._ai_chat_response(user_message, chat_history)

    def _ai_chat_response(self, user_message, chat_history):
        """Invoke OpenAI LLM as the intelligent Supervisor Router & Assistant."""
        try:
            client = OpenAI(api_key=get_api_key())
            
            # Formulate messages context
            system_prompt = f"""{self.role}
You have access to specialist domains:
- Health diagnostics and vital monitoring for cows, buffalos, goats, sheep, etc.
- Animal feed, hydration, and nutritional planning.
- Disease prevention and veterinary escalation criteria.

IMPORTANT GUIDELINES:
1. Always maintain a helpful, encouraging tone for farmers and caretakers.
2. Emphasize that you are an AI assistant and not a licensed veterinarian.
3. If user describes life-threatening signs (severe bloating, bleeding, collapse, extreme fever), urge immediate veterinary care.
4. Provide structured, actionable bullet points."""

            # Add past context safely (supports both dict format and tuple format)
            for turn in chat_history[-6:]:
                if isinstance(turn, dict):
                    role = turn.get("role", "user")
                    content = turn.get("content", "")
                    if role in ("user", "assistant") and content:
                        messages.append({"role": role, "content": content})
                elif isinstance(turn, (list, tuple)) and len(turn) == 2:
                    user_turn, bot_turn = turn
                    if user_turn:
                        messages.append({"role": "user", "content": str(user_turn)})
                    if bot_turn:
                        messages.append({"role": "assistant", "content": str(bot_turn)})
                
            messages.append({"role": "user", "content": user_message})
            
            response = client.chat.completions.create(
                model=APP_CONFIG["model"],
                messages=messages,
                max_tokens=APP_CONFIG["max_tokens"],
                temperature=0.5
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return self._demo_chat_response(user_message, user_message.lower(), error_msg=str(e))

    def _demo_chat_response(self, user_message, msg_lower, error_msg=None):
        """Intelligent rule-based fallback when no API key is provided."""
        disclaimer = f"\n\n---\n*{APP_CONFIG['safety_disclaimer']}*"
        
        if error_msg:
            prefix = f"*(Note: Running in offline fallback mode - {error_msg})*\n\n"
        else:
            prefix = "*(Running in Demo / Offline Agent Mode)*\n\n"
            
        if "not eating" in msg_lower or "appetite" in msg_lower or "anorexia" in msg_lower:
            return prefix + (
                "🐮 **Supervisor & Health Agent Analysis: Loss of Appetite (Anorexia)**\n\n"
                "When livestock stop eating, it is often an early indicator of systemic issues:\n"
                "1. **Check Body Temperature:** Normal cattle/buffalo temp is 37.8°C–39.2°C; goats/sheep are 38.5°C–39.7°C. High temperature indicates fever/infection.\n"
                "2. **Check Rumen Activity:** Listen for rumen contractions on the left flank (normal: 2–3 per 2 minutes).\n"
                "3. **Inspect Mouth & Teeth:** Check for oral lesions, ulcers (e.g. FMD), or foreign objects.\n"
                "4. **Feed Quality:** Check for spoiled, mouldy, or overly acidic silage.\n"
                "5. **Next Steps:** Offer fresh sweet grass or electrolyte water. If fasting exceeds 24–36 hours, contact a veterinarian immediately."
            ) + disclaimer

        elif "calf" in msg_lower or "lamb" in msg_lower or "kid" in msg_lower:
            return prefix + (
                "👶 **Supervisor & Nutrition Agent: Young Stock Care**\n\n"
                "Key monitoring essentials for calves, lambs, and kids:\n"
                "• **Colostrum intake:** Must receive high-quality colostrum within the first 2–6 hours of birth.\n"
                "• **Navel disinfection:** Clean with 7% iodine tincture to avoid joint ill/navel ill.\n"
                "• **Hydration & Scours:** Monitor stool consistency daily; scours (diarrhea) causes rapid dehydration.\n"
                "• **Temperature:** Young animals are vulnerable to hypothermia and pneumonia in draughty sheds."
            ) + disclaimer

        elif "veterinar" in msg_lower or "emergency" in msg_lower or "doctor" in msg_lower:
            return prefix + (
                "🚨 **Supervisor Agent: Red Flag Emergency Signs**\n\n"
                "Call a qualified veterinarian immediately if you observe:\n"
                "• Complete inability to stand (downer animal)\n"
                "• Severe left flank abdominal distension (acute bloat)\n"
                "• Rectal temperature > 40.5°C (105°F) or < 37.0°C\n"
                "• Labored breathing, open-mouth panting, or grunting\n"
                "• Active bleeding, prolapse, or sudden severe milk drop with swollen udder."
            ) + disclaimer

        elif "mastitis" in msg_lower or "milk" in msg_lower or "udder" in msg_lower:
            return prefix + (
                "🥛 **Health Specialist Agent: Mastitis & Udder Health**\n\n"
                "• **Signs:** Swollen, hot, or painful quarters, clots/flakes in milk, water-like milk, fever.\n"
                "• **Immediate Care:** Strip the affected quarter frequently, do California Mastitis Test (CMT), isolate milk.\n"
                "• **Consult Vet:** Prompt intramammary antibiotic or anti-inflammatory treatment prescribed by a vet prevents permanent quarter loss."
            ) + disclaimer

        else:
            return prefix + (
                f"🤖 **Supervisor Agent Response:**\n\n"
                f"I received your query: *\"{user_message}\"*\n\n"
                "As the Livestock Health Coordinator, I can help you with:\n"
                "• **Tab 2 (Add / Monitor Animal):** Perform comprehensive AI multi-agent health diagnostic with vitals and symptom scoring.\n"
                "• **Tab 4 (Health History):** Plot temperature and weight trajectory charts.\n"
                "• **Tab 5 (Health Report):** Generate printable formal livestock inspection reports.\n\n"
                "Ask me about specific animal symptoms, feeding strategies, vaccination schedules, or vital ranges!"
            ) + disclaimer
