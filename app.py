"""
Livestock Health Monitoring Assistant - Main Gradio Application
==============================================================
A multi-agent, AI-powered livestock health diagnostics & management platform.

Demonstrates core concepts from the Agentic AI syllabus:
- Multi-Agent Coordination (Supervisor, Health, Nutrition, Monitoring, Report Agents)
- Long-Term Agent Memory (SQLite persistent history)
- Agent Tools (Metric calculation, database queries, report & chart generation)
- State & Context Management
- Safe Fallback & Demo Mode
"""

import os
import gradio as gr
import pandas as pd
from datetime import datetime

from utils.config import APP_CONFIG, get_api_key, is_demo_mode, ANIMAL_TYPES, ACTIVITY_LEVELS, GENDER_OPTIONS
from utils.helpers import get_current_datetime, format_health_status
from database.database import LivestockDatabase
from agents.supervisor_agent import SupervisorAgent
from tools.report_tools import create_health_chart, generate_health_report
from tools.database_tools import get_dashboard_data, get_all_animal_ids, get_animal_history

# Initialize Database and seed sample records if empty
db = LivestockDatabase()
db.seed_sample_data()

# Initialize Chief Orchestrator
supervisor = SupervisorAgent()


# ===================================================================
# HANDLER FUNCTIONS FOR GRADIO
# ===================================================================

def fetch_dashboard_metrics():
    """Retrieve up-to-date metrics and recent records for the dashboard."""
    stats = db.get_dashboard_stats()
    
    total_animals = str(stats["total_animals"])
    healthy_count = str(stats["status_counts"]["Healthy"])
    monitoring_count = str(stats["status_counts"]["Needs Monitoring"])
    warning_count = str(stats["status_counts"]["Warning"] + stats["status_counts"]["Critical"])
    total_records = str(stats["total_records"])
    
    # Format recent records as DataFrame
    recent_records = stats.get("recent_records", [])
    if recent_records:
        df = pd.DataFrame(recent_records)
        df.rename(columns={
            "animal_id": "Animal ID",
            "animal_type": "Type",
            "health_status": "Status",
            "created_at": "Timestamp"
        }, inplace=True)
    else:
        df = pd.DataFrame(columns=["Animal ID", "Type", "Status", "Timestamp"])
        
    return total_animals, healthy_count, monitoring_count, warning_count, total_records, df


def search_livestock_records(search_term):
    """Filter livestock by ID or type."""
    if not search_term or search_term.strip() == "":
        return fetch_dashboard_metrics()[5]
    results = db.search_animals(search_term.strip())
    if results:
        df = pd.DataFrame(results)
        df = df[["animal_id", "animal_type", "breed", "age", "gender", "updated_at"]]
        df.rename(columns={
            "animal_id": "Animal ID",
            "animal_type": "Type",
            "breed": "Breed",
            "age": "Age",
            "gender": "Gender",
            "updated_at": "Last Updated"
        }, inplace=True)
        return df
    return pd.DataFrame(columns=["Animal ID", "Type", "Breed", "Age", "Gender", "Last Updated"])


def handle_health_analysis(animal_id, animal_type, breed, age, gender, weight,
                           temperature, food_intake, water_intake, activity_level,
                           symptoms, notes):
    """Execute the multi-agent diagnostic pipeline for an animal."""
    if not animal_id or animal_id.strip() == "":
        animal_id = f"{animal_type.upper()[:3]}-{datetime.now().strftime('%H%M%S')}"
        
    animal_data = {
        "animal_id": animal_id.strip(),
        "animal_type": animal_type,
        "breed": breed.strip() if breed else "Unknown",
        "age": age.strip() if age else "Unknown",
        "gender": gender,
        "weight": float(weight) if weight else 0.0,
        "temperature": float(temperature) if temperature else 0.0,
        "food_intake": food_intake,
        "water_intake": water_intake,
        "activity_level": activity_level,
        "symptoms": symptoms.strip() if symptoms else "None",
        "additional_notes": notes.strip() if notes else ""
    }
    
    # Process through Supervisor -> Specialist Agents
    result = supervisor.process_health_intake(animal_data)
    
    status_header = f"### {result['status_emoji']} Overall Health Status: **{result['health_status']}** (Risk Score: {result['health_result']['risk_score']}/10)"
    
    health_box = (
        f"#### 🏥 Health Analysis Agent Evaluation\n"
        f"• **Temperature:** {animal_data['temperature']}°C ({result['health_result']['temperature_status']})\n"
        f"• **Weight:** {animal_data['weight']} kg ({result['health_result']['weight_status']})\n"
        f"• **Symptoms Detected:** {', '.join(result['health_result']['symptoms_list']) if result['health_result']['symptoms_list'] else 'None'}\n\n"
        f"**Detailed Agent Analysis:**\n{result['health_result']['ai_analysis']}"
    )
    
    nutrition_box = (
        f"#### 🍽️ Nutrition Agent Guidance\n"
        f"{result['nutrition_result']['nutrition_advice']}"
    )
    
    monitoring_box = (
        f"#### 📊 Monitoring Agent Historical Analysis\n"
        f"{result['monitoring_result']['monitoring_notes']}"
    )
    
    report_box = (
        f"```text\n{result['report_result']['report_text']}\n```"
    )
    
    # Refresh animal ID list for other tabs
    updated_ids = gr.update(choices=get_all_animal_ids(), value=animal_data["animal_id"])
    
    return status_header, health_box, nutrition_box, monitoring_box, report_box, updated_ids, updated_ids


def handle_history_view(selected_animal_id, chart_type):
    """Retrieve animal history records and generate visualization charts."""
    if not selected_animal_id:
        return None, pd.DataFrame(), "Please select an Animal ID."
        
    records = db.get_animal_history(selected_animal_id)
    if not records:
        return None, pd.DataFrame(), f"No records found for {selected_animal_id}."
        
    # Generate Matplotlib chart
    chart_res = create_health_chart(selected_animal_id, records, chart_type=chart_type.lower())
    chart_path = chart_res.get("chart_path")
    
    df = pd.DataFrame(records)
    display_cols = ["created_at", "temperature", "weight", "health_status", "symptoms", "food_intake", "activity_level"]
    available_cols = [c for c in display_cols if c in df.columns]
    df = df[available_cols].rename(columns={
        "created_at": "Date/Time",
        "temperature": "Temp (°C)",
        "weight": "Weight (kg)",
        "health_status": "Status",
        "symptoms": "Symptoms",
        "food_intake": "Feed Intake",
        "activity_level": "Activity"
    })
    
    info_msg = f"Showing {len(records)} historical checkups for {selected_animal_id}."
    return chart_path, df, info_msg


def handle_report_export(selected_animal_id):
    """Export formatted health report for the chosen animal."""
    if not selected_animal_id:
        return "Please select an animal ID to export a report.", None
        
    records = db.get_animal_history(selected_animal_id)
    if not records:
        return f"No records found for {selected_animal_id}.", None
        
    latest = records[0]
    report_res = generate_health_report(
        animal_data=latest,
        health_analysis=latest.get("health_analysis", "Routine checkup."),
        nutrition_advice=latest.get("nutrition_advice", "Standard feeding."),
        monitoring_notes=latest.get("monitoring_notes", "Stable."),
        history=records
    )
    
    return report_res["report_text"], report_res.get("report_file")


def handle_chat(user_message, history):
    """Handle conversational chat turns with the Supervisor Agent."""
    if history is None:
        history = []
    if not user_message or user_message.strip() == "":
        return "", history
        
    bot_response = supervisor.chat(user_message, history)
    
    # Modern Gradio (4.x / 5.x) expects [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}]
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": bot_response})
    return "", history


# ===================================================================
# PRESET LOADERS FOR EASY DEMO
# ===================================================================

def load_cow_demo():
    return (
        "COW-001", "Cow", "Holstein Friesian", "4 years", "Female",
        465.0, 40.2, "Reduced", "Reduced", "Very Low",
        "Not eating, weakness and reduced milk production",
        "Third day of reduced appetite, suspecting mastitis or viral fever."
    )

def load_buffalo_demo():
    return (
        "BUF-001", "Buffalo", "Murrah", "5 years", "Female",
        550.0, 38.3, "Normal", "Normal", "Normal",
        "None",
        "Routine seasonal checkup and deworming follow-up."
    )

def load_goat_demo():
    return (
        "GOAT-001", "Goat", "Beetal", "2 years", "Male",
        46.5, 39.9, "Reduced", "Normal", "Reduced",
        "Coughing, nasal discharge, shivering in the evening",
        "Sudden weather dip after heavy rainfall."
    )


# ===================================================================
# GRADIO UI DEFINITION
# ===================================================================

custom_theme = gr.themes.Soft(
    primary_hue="emerald",
    secondary_hue="teal",
    neutral_hue="slate"
)

with gr.Blocks(title="Livestock Health Monitoring Assistant") as demo:
    
    # ── Header & Banner ──
    with gr.Row():
        with gr.Column(scale=9):
            gr.Markdown(
                """
                # 🐄 Livestock Health Monitoring Assistant
                ### *AI-Powered Multi-Agent Veterinary Health Diagnostics & Memory System*
                """
            )
        with gr.Column(scale=3):
            mode_badge = "🟢 **Mode:** Live OpenAI API" if not is_demo_mode() else "🟠 **Mode:** Demo / Offline Agentic Fallback"
            gr.Markdown(f"### System Status\n{mode_badge}\n*Agent Memory: SQLite Active*")
    
    gr.Markdown("---")
    
    # ── Tabs Container ──
    with gr.Tabs() as tabs:
        
        # ──────────────────────────────────────────────────────────
        # TAB 1: 🏠 DASHBOARD
        # ──────────────────────────────────────────────────────────
        with gr.TabItem("🏠 Dashboard", id="tab_dash"):
            gr.Markdown("### 📊 Farm Health Overview & Real-Time Analytics")
            
            with gr.Row():
                kpi_total = gr.Textbox(label="Total Animals", value="...", interactive=False)
                kpi_healthy = gr.Textbox(label="🟢 Healthy", value="...", interactive=False)
                kpi_monitor = gr.Textbox(label="🟡 Needs Monitoring", value="...", interactive=False)
                kpi_warning = gr.Textbox(label="🔴 Warning / Critical", value="...", interactive=False)
                kpi_records = gr.Textbox(label="📋 Total Checkups", value="...", interactive=False)
                
            with gr.Row():
                with gr.Column(scale=8):
                    search_input = gr.Textbox(
                        label="🔍 Search Livestock by ID, Type, or Breed", 
                        placeholder="Type COW, Murrah, Beetal..."
                    )
                with gr.Column(scale=2):
                    refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="secondary")
            
            recent_table = gr.DataFrame(
                label="Recent Health Checkup Records (SQLite Persistent Memory)",
                headers=["Animal ID", "Type", "Status", "Timestamp"],
                interactive=False
            )
            
            refresh_btn.click(
                fn=fetch_dashboard_metrics,
                inputs=[],
                outputs=[kpi_total, kpi_healthy, kpi_monitor, kpi_warning, kpi_records, recent_table]
            )
            search_input.change(
                fn=search_livestock_records,
                inputs=[search_input],
                outputs=[recent_table]
            )

        # ──────────────────────────────────────────────────────────
        # TAB 2: 🐄 ADD / MONITOR ANIMAL
        # ──────────────────────────────────────────────────────────
        with gr.TabItem("🐄 Add / Monitor Animal", id="tab_monitor"):
            gr.Markdown("### 🩺 Multi-Agent Diagnostic Intake & Assessment")
            
            with gr.Row():
                gr.Markdown("**Quick Demo Presets (Click to Auto-fill):**")
                demo_cow_btn = gr.Button("🐄 Sick Cow (Fever & Milk Drop)", size="sm")
                demo_buf_btn = gr.Button("🐃 Healthy Murrah Buffalo", size="sm")
                demo_goat_btn = gr.Button("🐐 Sick Goat (Cough & Discharge)", size="sm")
                
            with gr.Row():
                with gr.Column(scale=6):
                    gr.Markdown("#### 📋 1. Identification & Vitals")
                    in_id = gr.Textbox(label="Animal ID", placeholder="e.g. COW-001, GOAT-002", value="COW-001")
                    with gr.Row():
                        in_type = gr.Dropdown(choices=ANIMAL_TYPES, label="Animal Type", value="Cow")
                        in_breed = gr.Textbox(label="Breed", placeholder="e.g. Holstein, Murrah", value="Holstein Friesian")
                    with gr.Row():
                        in_age = gr.Textbox(label="Age", placeholder="e.g. 4 years, 8 months", value="4 years")
                        in_gender = gr.Dropdown(choices=GENDER_OPTIONS, label="Gender", value="Female")
                    with gr.Row():
                        in_weight = gr.Number(label="Weight (kg)", value=468.0)
                        in_temp = gr.Number(label="Body Temperature (°C)", value=40.2)
                        
                    gr.Markdown("#### 🌾 2. Appetite, Behavior & Symptoms")
                    with gr.Row():
                        in_food = gr.Dropdown(choices=["Normal", "Reduced", "Very Low", "None"], label="Food Intake", value="Reduced")
                        in_water = gr.Dropdown(choices=["Normal", "Reduced", "Very Low", "None"], label="Water Intake", value="Reduced")
                        in_activity = gr.Dropdown(choices=ACTIVITY_LEVELS, label="Activity Level", value="Very Low")
                        
                    in_symptoms = gr.Textbox(
                        label="Symptoms (Separate with commas)", 
                        placeholder="e.g. Not eating, weakness, reduced milk production, shivering",
                        value="Not eating, weakness and reduced milk production",
                        lines=2
                    )
                    in_notes = gr.Textbox(
                        label="Additional Field Notes",
                        placeholder="e.g. Weather changes, sudden feed switch, vaccinations...",
                        lines=2
                    )
                    
                    analyze_btn = gr.Button("🚀 Run Multi-Agent Health Analysis", variant="primary", size="lg")

                with gr.Column(scale=6):
                    gr.Markdown("#### 🤖 Agentic Workflow Outputs")
                    out_status = gr.Markdown("### ⚪ Ready for Assessment")
                    out_health = gr.Markdown("*Health Analysis Agent results will appear here...*")
                    out_nutrition = gr.Markdown("*Nutrition Agent dietary guidance will appear here...*")
                    out_monitoring = gr.Markdown("*Monitoring Agent trend comparisons will appear here...*")
                    with gr.Accordion("📄 Full Generated Health Report", open=False):
                        out_report = gr.Markdown("*Generated report preview...*")

            # Presets event wiring
            demo_cow_btn.click(
                fn=load_cow_demo,
                inputs=[],
                outputs=[in_id, in_type, in_breed, in_age, in_gender, in_weight, in_temp, in_food, in_water, in_activity, in_symptoms, in_notes]
            )
            demo_buf_btn.click(
                fn=load_buffalo_demo,
                inputs=[],
                outputs=[in_id, in_type, in_breed, in_age, in_gender, in_weight, in_temp, in_food, in_water, in_activity, in_symptoms, in_notes]
            )
            demo_goat_btn.click(
                fn=load_goat_demo,
                inputs=[],
                outputs=[in_id, in_type, in_breed, in_age, in_gender, in_weight, in_temp, in_food, in_water, in_activity, in_symptoms, in_notes]
            )

        # ──────────────────────────────────────────────────────────
        # TAB 3: 🤖 AI ASSISTANT (CHAT)
        # ──────────────────────────────────────────────────────────
        with gr.TabItem("🤖 AI Assistant", id="tab_chat"):
            gr.Markdown("### 💬 Conversational Livestock Veterinary Advisor")
            gr.Markdown("Ask the Supervisor Agent anything about livestock diseases, feed management, calf care, or emergency symptoms.")
            
            chatbot = gr.Chatbot(height=450, show_label=False)
            
            with gr.Row():
                chat_msg = gr.Textbox(
                    placeholder="Type your question here... (e.g. Why is my cow not eating?)",
                    label="Your Query",
                    scale=9
                )
                chat_send = gr.Button("Ask Assistant", variant="primary", scale=2)
                chat_clear = gr.Button("Clear", scale=1)
                
            gr.Markdown("#### 💡 Try Asking:")
            with gr.Row():
                sample_q1 = gr.Button("Why is my cow not eating?", size="sm")
                sample_q2 = gr.Button("What are warning signs of mastitis?", size="sm")
                sample_q3 = gr.Button("How to care for a newborn calf?", size="sm")
                sample_q4 = gr.Button("What are signs of emergency veterinary care?", size="sm")
                
            chat_send.click(fn=handle_chat, inputs=[chat_msg, chatbot], outputs=[chat_msg, chatbot])
            chat_msg.submit(fn=handle_chat, inputs=[chat_msg, chatbot], outputs=[chat_msg, chatbot])
            chat_clear.click(lambda: [], None, chatbot, queue=False)
            
            sample_q1.click(lambda: "Why is my cow not eating?", None, chat_msg)
            sample_q2.click(lambda: "What are warning signs of mastitis?", None, chat_msg)
            sample_q3.click(lambda: "How to care for a newborn calf?", None, chat_msg)
            sample_q4.click(lambda: "What are signs of emergency veterinary care?", None, chat_msg)

        # ──────────────────────────────────────────────────────────
        # TAB 4: 📊 HEALTH HISTORY & CHARTS
        # ──────────────────────────────────────────────────────────
        with gr.TabItem("📊 Health History", id="tab_history"):
            gr.Markdown("### 📈 Longitudinal Health & Vitals Trajectory")
            
            with gr.Row():
                hist_animal_id = gr.Dropdown(
                    choices=get_all_animal_ids(), 
                    label="Select Animal ID", 
                    value=get_all_animal_ids()[0] if get_all_animal_ids() else "COW-001"
                )
                hist_chart_type = gr.Radio(
                    choices=["Combined", "Temperature", "Weight"],
                    label="Chart Type",
                    value="Combined"
                )
                hist_plot_btn = gr.Button("📊 Generate Charts & History", variant="primary")
                
            hist_status_msg = gr.Markdown("Select an animal and click 'Generate Charts'")
            
            with gr.Row():
                chart_output = gr.Image(label="Matplotlib Health Trajectory Chart", type="filepath")
                
            hist_table = gr.DataFrame(
                label="Historical Checkup Records for Selected Animal",
                interactive=False
            )
            
            hist_plot_btn.click(
                fn=handle_history_view,
                inputs=[hist_animal_id, hist_chart_type],
                outputs=[chart_output, hist_table, hist_status_msg]
            )

        # ──────────────────────────────────────────────────────────
        # TAB 5: 📄 HEALTH REPORT
        # ──────────────────────────────────────────────────────────
        with gr.TabItem("📄 Health Report", id="tab_report"):
            gr.Markdown("### 📋 Formal Livestock Health Inspection Report")
            gr.Markdown("Generate, review, and download official health monitoring reports compiled by the Report Agent.")
            
            with gr.Row():
                rep_animal_id = gr.Dropdown(
                    choices=get_all_animal_ids(),
                    label="Select Animal ID for Report",
                    value=get_all_animal_ids()[0] if get_all_animal_ids() else "COW-001"
                )
                rep_gen_btn = gr.Button("📑 Generate Official Report", variant="primary")
                
            report_display = gr.Textbox(
                label="Official Report Document Preview",
                lines=18,
                interactive=False
            )
            
            report_file_out = gr.File(label="📥 Download Printable Report (.txt)")
            
            rep_gen_btn.click(
                fn=handle_report_export,
                inputs=[rep_animal_id],
                outputs=[report_display, report_file_out]
            )

    # ── Analyze Button Execution Wiring ──
    analyze_btn.click(
        fn=handle_health_analysis,
        inputs=[
            in_id, in_type, in_breed, in_age, in_gender, in_weight, in_temp,
            in_food, in_water, in_activity, in_symptoms, in_notes
        ],
        outputs=[
            out_status, out_health, out_nutrition, out_monitoring, out_report,
            hist_animal_id, rep_animal_id
        ]
    )
    
    # ── Initial Load Event ──
    demo.load(
        fn=fetch_dashboard_metrics,
        inputs=[],
        outputs=[kpi_total, kpi_healthy, kpi_monitor, kpi_warning, kpi_records, recent_table]
    )

    # ── Footer ──
    gr.Markdown("---")
    gr.Markdown(
        f"<center><small><b>{APP_CONFIG['safety_disclaimer']}</b><br>"
        f"Livestock Health Monitoring Assistant | College Mini-Project | Agentic AI & Automation</small></center>"
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    server_name = os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0")
    
    print("=" * 60)
    print("🐄 LIVESTOCK HEALTH MONITORING ASSISTANT")
    print("=" * 60)
    print(f"• Mode: {'Live OpenAI API' if not is_demo_mode() else 'Demo / Offline Fallback Mode'}")
    print(f"• SQLite Database: {APP_CONFIG['database_path']}")
    print(f"• Server binding: http://{server_name}:{port}")
    print("=" * 60)
    
    # Launch application (works both locally and on Render cloud)
    demo.launch(theme=custom_theme, server_name=server_name, server_port=port, share=False)
