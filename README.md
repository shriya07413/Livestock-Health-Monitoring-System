# 🐄 Livestock Health Monitoring Assistant
> **An Agentic AI Multi-Agent System for Veterinary Health Diagnostics, Longitudinal Monitoring, and Intelligent Farm Assistance.**

---

## 📖 Table of Contents
1. [Project Title](#1-project-title)
2. [Project Overview](#2-project-overview)
3. [Problem Statement](#3-problem-statement)
4. [Project Objectives](#4-project-objectives)
5. [Key Features](#5-key-features)
6. [Technologies Used](#6-technologies-used)
7. [Agent Architecture](#7-agent-architecture)
8. [How the Agents Work](#8-how-the-agents-work)
9. [How Memory Works](#9-how-memory-works)
10. [How Tools Work](#10-how-tools-work)
11. [How Gradio Works](#11-how-gradio-works)
12. [How API Integration Works](#12-how-api-integration-works)
13. [Project Folder Structure](#13-project-folder-structure)
14. [Installation Requirements](#14-installation-requirements)
15. [Python Installation](#15-python-installation)
16. [Virtual Environment Setup](#16-virtual-environment-setup)
17. [Installing Dependencies](#17-installing-dependencies)
18. [Creating .env](#18-creating-env)
19. [Adding API Key & Secret Management](#19-adding-api-key--secret-management)
20. [Running the Project](#20-running-the-project)
21. [How to Use the Application](#21-how-to-use-the-application)
22. [Example Input](#22-example-input)
23. [Expected Output](#23-expected-output)
24. [Troubleshooting](#24-troubleshooting)
25. [Common Errors and Solutions](#25-common-errors-and-solutions)
26. [How to Change the API Key](#26-how-to-change-the-api-key)
27. [How SQLite Database Works](#27-how-sqlite-database-works)
28. [How to Add Another Agent](#28-how-to-add-another-agent)
29. [How to Add Another Tool](#29-how-to-add-another-tool)
30. [How to Modify the UI](#30-how-to-modify-the-ui)
31. [Syllabus Mapping](#31-syllabus-mapping)
32. [Viva Explanation](#32-viva-explanation)
33. [Important Concepts to Understand](#33-important-concepts-to-understand)
34. [Limitations](#34-limitations)
35. [Future Enhancements](#35-future-enhancements)

---

### 1. Project Title
**Livestock Health Monitoring Assistant** — A Multi-Agent AI System with Persistent Memory and Decision Support for Livestock Caretakers.

### 2. Project Overview
The Livestock Health Monitoring Assistant is an academic mini-project developed for the **Agentic AI & Automation** course. It demonstrates how autonomous AI agents collaborate to evaluate livestock health parameters, calculate risk factors, remember past medical histories, formulate nutrition plans, and generate audit reports.

### 3. Problem Statement
Smallholders, farmers, and dairy managers often lack 24/7 on-demand access to veterinary professionals. Early symptoms (mild fever, decreased milk yield, slight lethargy) go unnoticed until diseases become acute. Traditional single-prompt chatbots lack persistent memory, fail to track changes over time, and cannot safely invoke calculation tools.

### 4. Project Objectives
- Demonstrate a multi-agent hierarchy (Supervisor + Specialist Workers).
- Implement persistent agent memory via SQLite for longitudinal health tracking.
- Equip agents with deterministic calculation, storage, and visualization tools.
- Provide a clean, modern web interface with Gradio.
- Ensure strict safety guardrails and graceful offline fallback.

### 5. Key Features
- **🏠 Farm Health Dashboard:** Real-time KPI summary (Total animals, normal/healthy, needs monitoring, warnings) and animal search.
- **🐄 Multi-Agent Health Intake:** Inputs for vitals (temperature, weight), feeding behavior, and symptoms with instant multi-agent breakdown.
- **🤖 Conversational AI Assistant:** Specialized Q&A agent for disease indicators, emergency signs, and calf care.
- **📊 Longitudinal Charts:** Matplotlib trend visualization for temperature and weight over time with normal health range bands.
- **📄 Formal Health Reports:** Formatted printable inspection reports with downloadable text export.
- **⚡ Safe Demo Mode:** Full offline functionality even without an OpenAI API key.

### 6. Technologies Used
- **Python 3.9+:** Core programming language.
- **Gradio:** Interactive web GUI dashboard.
- **OpenAI API (GPT-4o-mini):** Cognitive engine for agent reasoning and conversational advice.
- **SQLite3:** Embedded relational database for agent memory.
- **Pandas:** Tabular record manipulation and transformation.
- **Matplotlib:** Statistical health charting and visual trends.
- **python-dotenv:** Secure environment variable management.

---

### 7. Agent Architecture

```
                       ┌─────────────────────────┐
                       │   Farmer / User (GUI)   │
                       └────────────┬────────────┘
                                    │
                                    ▼
                       ┌─────────────────────────┐
                       │    Supervisor Agent     │
                       └────────────┬────────────┘
         ┌──────────────────┬───────┴──────────┬──────────────────┐
         ▼                  ▼                  ▼                  ▼
┌─────────────────┐┌─────────────────┐┌─────────────────┐┌─────────────────┐
│  Health Agent   ││ Monitoring Agent││ Nutrition Agent ││  Report Agent   │
│ (Vitals/Symptoms││(Memory History/ ││ (Diet/Hydration ││(Formulate Report│
│  Diagnostics)   ││ Trend Detection)││  Guidance)      ││  & Export Docs) │
└────────┬────────┘└────────┬────────┘└────────┬────────┘└────────┬────────┘
         │                  │                  │                  │
         └──────────────────┼──────────────────┴──────────────────┘
                            ▼
               ┌───────────────────────────┐
               │    Deterministic Tools    │
               │ • calculate_health_metrics│
               │ • get_animal_history      │
               │ • save_health_record      │
               │ • create_health_chart     │
               └────────────┬──────────────┘
                            ▼
               ┌───────────────────────────┐
               │  SQLite Long-Term Memory  │
               │    (livestock.db)         │
               └───────────────────────────┘
```

---

### 8. How the Agents Work
1. **Supervisor Agent (`supervisor_agent.py`):** The team leader. It receives the user's input, directs the workflow sequence, routes questions, and aggregates results.
2. **Health Analysis Agent (`health_agent.py`):** Evaluates vital signs against species-specific reference tables, calculates risk scores, and checks for fever or hypothermia.
3. **Monitoring Agent (`monitoring_agent.py`):** Queries SQLite memory to compare current readings against previous visits, detecting temperature spikes or weight drop trends.
4. **Nutrition Agent (`nutrition_agent.py`):** Estimates daily dry matter intake (approx. 2.5% of body weight for cattle) and suggests dietary adaptations.
5. **Report Agent (`report_agent.py`):** Formats all findings into a clean inspection document.

### 9. How Memory Works
- **Short-Term Memory:** Stored in the execution state dictionary and Gradio chat context.
- **Long-Term Memory:** Handled by `database/database.py` with SQLite. Every health intake creates a new timestamped row in `health_records`. When the Monitoring Agent runs, it queries this table to identify trends over time.

### 10. How Tools Work
Agents do not do raw arithmetic or database operations inside LLM prompts. Instead, they call structured Python functions:
- `calculate_health_metrics(...)`
- `save_health_record(...)`
- `get_animal_history(...)`
- `create_health_chart(...)`
- `generate_health_report(...)`

### 11. How Gradio Works
`app.py` builds an intuitive 5-tab reactive interface using `gr.Blocks`. When buttons are clicked, Gradio invokes backend Python functions and updates the corresponding UI components.

### 12. How API Integration Works
The application uses the official `openai` SDK. When an API key is present in `.env`, the system sends structured prompts with system personas. If no key is present, the app automatically switches to **Demo Mode**, utilizing rule-based logic without crashing.

---

### 13. Project Folder Structure

```
livestock-health-monitoring-assistant/
├── app.py                      # Main Gradio Web Application
├── agents/                     # Multi-Agent Implementations
│   ├── __init__.py
│   ├── supervisor_agent.py     # Chief Orchestrator & Chatbot
│   ├── health_agent.py         # Health Diagnostics Specialist
│   ├── nutrition_agent.py      # Dietary & Feeding Specialist
│   ├── monitoring_agent.py     # Historical Memory Specialist
│   └── report_agent.py         # Documentation Specialist
├── tools/                      # Deterministic Agent Tools
│   ├── __init__.py
│   ├── database_tools.py       # CRUD & Memory Tools
│   ├── health_tools.py         # Metric & Knowledge Calculation Tools
│   └── report_tools.py         # Matplotlib Charting & Export Tools
├── database/                   # SQLite Persistent Layer
│   ├── __init__.py
│   ├── database.py             # Database Manager & Schema
│   └── livestock.db            # Auto-generated SQLite Database
├── utils/                      # Utilities & Configuration
│   ├── __init__.py
│   ├── config.py               # Environment & App Settings
│   └── helpers.py              # Parsing & Validation Helpers
├── data/
│   └── sample_livestock.csv    # Seed Dataset
├── reports/                    # Generated Inspection Reports
├── charts/                     # Generated Matplotlib Plots
├── .env                        # Local Secret API Keys (Git Ignored)
├── .env.example                # Example Environment Template
├── .gitignore                  # Git Ignore Configuration
├── requirements.txt            # Python Dependencies
├── README.md                   # Complete Project Documentation
├── BEGINNER_GUIDE.md           # Zero-to-Hero AI & Agent Concepts
├── SYLLABUS_MAPPING.md         # Course Curriculum Cross-Reference
└── VIVA_QUESTIONS.md           # 35+ Viva Exam Q&A Guide
```

---

### 14. Installation Requirements
- Python 3.9, 3.10, 3.11, or 3.12
- Internet access (for installing packages; running can be offline in demo mode)
- Web browser (Chrome, Safari, Edge, Firefox)

### 15. Python Installation
- **macOS:** Install via [Homebrew](https://brew.sh) (`brew install python`) or download from [python.org](https://www.python.org).
- **Windows:** Download Python from [python.org](https://www.python.org). **Check "Add Python to PATH" during setup.**

### 16. Virtual Environment Setup

**On macOS / Linux:**
```bash
cd livestock-health-monitoring-assistant
python3 -m venv venv
source venv/bin/activate
```

**On Windows (Command Prompt / PowerShell):**
```cmd
cd livestock-health-monitoring-assistant
python -m venv venv
venv\Scripts\activate
```

### 17. Installing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 18. Creating .env
If not already created, copy `.env.example`:
```bash
cp .env.example .env
```

### 19. Adding API Key & Secret Management
Open `.env` in any text editor and paste your key:
```ini
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
*If you don't have an API key, leave it as `OPENAI_API_KEY=your_api_key_here`. The application will safely launch in **Demo Mode**!*

---

### 20. Running the Project
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:7860
```

---

### 21. How to Use the Application
1. **View Overview:** Open Tab 1 (`🏠 Dashboard`) to view registered animals and recent records.
2. **Run Diagnostic:** Go to Tab 2 (`🐄 Add / Monitor Animal`), click **"Sick Cow (Fever & Milk Drop)"** to populate the fields, and click **"Run Multi-Agent Health Analysis"**.
3. **Chat with AI:** Switch to Tab 3 (`🤖 AI Assistant`) and ask questions about livestock care.
4. **View Trends:** Go to Tab 4 (`📊 Health History`), pick `COW-001`, and click **"Generate Charts & History"**.
5. **Export Report:** Go to Tab 5 (`📄 Health Report`), pick `COW-001`, and click **"Generate Official Report"**.

### 22. Example Input
- **Animal ID:** `COW-001`
- **Animal Type:** `Cow`
- **Breed:** `Holstein Friesian`
- **Age:** `4 years`
- **Weight:** `468 kg`
- **Temperature:** `40.2°C`
- **Symptoms:** `Not eating, weakness and reduced milk production`

### 23. Expected Output
- **Health Status:** 🟠 `Warning` (Risk Score: 5.5/10)
- **Health Agent:** High fever detected (40.2°C > 39.2°C normal max). Reduced milk production and weakness noted.
- **Monitoring Agent:** Temperature increased from 39.1°C to 40.2°C (+1.1°C); weight dropped by 7 kg over 4 days.
- **Nutrition Agent:** High hydration requirement, electrolyte replenishment, easily digestible green fodder.
- **Report Agent:** Compiled formal inspection document saved to `reports/`.

---

### 24. Troubleshooting
- **Port in use (7860):** Run `python app.py` with another port or close previous instances.
- **ModuleNotFoundError:** Ensure virtual environment is activated (`source venv/bin/activate`).
- **Gradio does not open:** Open `http://127.0.0.1:7860` manually in your browser.

### 25. Common Errors and Solutions
| Error | Cause | Solution |
|---|---|---|
| `OpenAI AuthenticationError` | Expired or incorrect API key in `.env` | Verify your key at [platform.openai.com](https://platform.openai.com) or use demo mode. |
| `sqlite3.OperationalError` | Database file permissions | Delete `database/livestock.db` to let the app auto-recreate it. |
| `No module named 'gradio'` | Dependencies not installed in active environment | Run `pip install -r requirements.txt`. |

### 26. How to Change the API Key
Edit the `.env` file directly:
```ini
OPENAI_API_KEY=sk-newkeyhere...
```
Restart `app.py`.

### 27. How SQLite Database Works
SQLite stores all tables in `database/livestock.db`. It requires no server process. Schema tables:
- `animals`: Master catalog of animal profiles.
- `health_records`: Time-series transactional log of checkups, vitals, and agent findings.

### 28. How to Add Another Agent
1. Create a new file in `agents/` (e.g. `agents/vaccination_agent.py`).
2. Define the agent class and its role.
3. Import and instantiate it inside `agents/supervisor_agent.py`.
4. Call it inside `process_health_intake()`.

### 29. How to Add Another Tool
1. Define a standard Python function in `tools/` (e.g. `tools/weather_tools.py`).
2. Import and invoke the function from the appropriate agent.

### 30. How to Modify the UI
Open `app.py` and modify the components within `with gr.Blocks()` or change the color theme using `gr.themes`.

### 31. Syllabus Mapping
See [SYLLABUS_MAPPING.md](SYLLABUS_MAPPING.md) for full curriculum cross-referencing.

### 32. Viva Explanation
Read [VIVA_QUESTIONS.md](VIVA_QUESTIONS.md) for 35+ ready-to-answer examination questions.

### 33. Important Concepts to Understand
- **Agentic AI:** Autonomous agents that plan, reason, invoke tools, and maintain state.
- **Supervisor Pattern:** Central coordinator directing specialized sub-agents.
- **Agent Memory:** Distinguishing between transient session context and persistent database logs.
- **Guardrails:** Ensuring AI does not replace veterinarians or prescribe dangerous medication.

### 34. Limitations
- Not a replacement for a certified veterinary doctor.
- Visual inspection (image analysis) is not included in this text/numerical version.
- Offline mode uses deterministic domain heuristics.

### 35. Future Enhancements
- Integration of Computer Vision (YOLO) for detecting skin lesions or limping.
- IoT Collar Integration (ESP32/Raspberry Pi temperature & rumination sensors).
- SMS/WhatsApp alert dispatch for critical livestock warnings.
