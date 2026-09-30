# 🎓 Viva Preparation: 35+ Questions & Model Answers
> **Course:** Agentic AI & Automation  
> **Project:** Livestock Health Monitoring Assistant

---

### Q1. What is the core objective of your project?
**Answer:** The objective is to build an Agentic AI system that assists livestock caretakers by monitoring animal health, diagnosing potential concerns from vital signs and symptoms, tracking longitudinal health changes using persistent memory, providing dietary guidance, and compiling formal inspection reports.

### Q2. What is Agentic AI, and how is it different from a conventional chatbot?
**Answer:** A conventional chatbot only predicts the next tokens of text in a single conversational thread and cannot perform real-world actions. Agentic AI involves autonomous software entities (agents) that possess defined roles, plan execution steps, invoke external tools (databases, math calculations, charts), maintain persistent state and memory, and collaborate in multi-agent workflows.

### Q3. Why did you use a Multi-Agent architecture instead of a single prompt?
**Answer:** In complex domains like veterinary health, a single prompt easily suffers from hallucinations, context overflow, and lack of focus. Decomposing the system into specialized agents (Health, Monitoring, Nutrition, Report) under a Supervisor enforces the separation of concerns, improves accuracy, and allows each agent to utilize specific tools.

### Q4. What is the role of the Supervisor Agent?
**Answer:** The Supervisor Agent acts as the central coordinator. It receives user inputs, analyzes the intent, executes the multi-agent workflow graph, routes queries to the appropriate specialist agents, and aggregates their findings into a cohesive final output.

### Q5. What is the Health Analysis Agent responsible for?
**Answer:** It assesses vital signs (rectal temperature, weight) against species-specific physiological reference ranges, analyzes reported symptoms, calculates an objective risk score (0 to 10), and produces an educational health diagnostic.

### Q6. How does the Monitoring Agent utilize "Agent Memory"?
**Answer:** The Monitoring Agent uses SQLite as long-term persistent memory. When evaluating an animal, it queries past checkup records using the `get_animal_history()` tool and calculates delta metrics (e.g., temperature spike of +1.1°C or weight drop of 7kg), allowing it to identify whether an animal's condition is improving, stable, or declining over time.

### Q7. What is the function of the Nutrition Agent?
**Answer:** The Nutrition Agent provides species-tailored feeding guidelines and hydration requirements. For example, for cattle it calculates estimated dry matter intake (~2.5% of body weight) and adjusts dietary recommendations based on whether the animal has fever, reduced appetite, or lactation demands.

### Q8. What does the Report Agent do?
**Answer:** The Report Agent consolidates the outputs of the Health, Nutrition, and Monitoring agents, embeds timestamp metadata, and uses the `generate_health_report()` tool to compile a formatted document that can be previewed or downloaded.

### Q9. What are "Tools" in Agentic AI, and what tools did you implement?
**Answer:** Tools are deterministic executable functions that agents can invoke. In this project, we implemented:
1. `calculate_health_metrics()`: Math and threshold evaluation.
2. `save_health_record()`: SQLite database write.
3. `get_animal_history()`: SQLite database query.
4. `create_health_chart()`: Matplotlib trend rendering.
5. `generate_health_report()`: Structured text compilation.
6. `get_health_knowledge()`: Domain knowledge base retrieval.

### Q10. Why is SQLite used instead of standard text or JSON files?
**Answer:** SQLite is an embedded relational database that provides ACID compliance, fast SQL indexing, structured schema validation, and persistent storage without requiring a separate server daemon.

### Q11. What is the difference between Agent State and Agent Memory?
**Answer:** 
- **Agent State:** The temporary data snapshot held in memory during the execution of a single workflow (e.g., current animal ID, current risk score).
- **Agent Memory:** Information stored across time that persists even after the workflow finishes (e.g., historical medical logs in SQLite).

### Q12. How does your system ensure veterinary safety and ethics?
**Answer:** 
1. Every report and diagnostic output includes an explicit disclaimer stating that the system is an educational decision-support tool, not a replacement for a licensed veterinarian.
2. If critical red-flag symptoms are detected (severe fever, bleeding, collapse), the system immediately advises urgent veterinary intervention.
3. The agents are barred from prescribing dangerous medical dosages or controlled pharmaceuticals.

### Q13. How does API key management work, and why should keys never be hardcoded?
**Answer:** Keys are stored in an external `.env` file and loaded using `python-dotenv`. The `.env` file is excluded from version control via `.gitignore`. Hardcoding keys in source code risks exposing paid credentials if pushed to public repositories like GitHub.

### Q14. What happens if there is no internet connection or the OpenAI API key is missing?
**Answer:** The application features a built-in **Safe Demo / Offline Fallback Mode**. If no valid API key is detected, the `SupervisorAgent` automatically switches to deterministic rule-based algorithms, ensuring all UI tabs, database logging, and charting functions work seamlessly.

### Q15. Why did you choose Gradio for the GUI?
**Answer:** Gradio enables rapid development of reactive, web-based UI dashboards in pure Python. It natively supports dataframes, real-time plotting, dropdowns, and chat interfaces without requiring separate JavaScript/React frontends.

### Q16. How are the Matplotlib health charts generated?
**Answer:** The `create_health_chart()` tool queries historical records for a specific animal ID, sorts them chronologically, and plots temperature and weight trajectories over time. It also shades the species-specific normal range (e.g. 37.8°C–39.2°C for cows) to provide immediate visual context.

### Q17. How does the system handle different livestock species?
**Answer:** The system maintains a species-specific lookup configuration (`APP_CONFIG`) containing physiological baselines (temperature, weight, and nutritional needs) for Cows, Buffalos, Goats, Sheep, Horses, Pigs, and Poultry.

### Q18. What is the risk score calculation formula?
**Answer:** The `calculate_health_metrics()` function assigns weighted scores based on:
- Deviation from normal temperature (+2 to +4 points)
- Underweight or overweight deviation (+1 to +3 points)
- Critical keyword presence in symptoms (+3 points per critical sign)
- Food/water intake reduction (+2 points each)
A score of 0 is Healthy, $\le 3$ is Needs Monitoring, $\le 6$ is Warning, and $>6$ is Critical.

### Q19. How did you structure your Python project?
**Answer:** We used a modular architecture with distinct packages:
- `agents/`: Agent implementations.
- `tools/`: Callable functions.
- `database/`: Database schema and SQLite connection manager.
- `utils/`: Configuration and helper routines.
- `data/`, `reports/`, `charts/`: Seed data and generated artifacts.
- `app.py`: Main entry point.

### Q20. Can you explain how the workflow executes when a user clicks "Analyze Animal Health"?
**Answer:**
1. `app.py` packages form inputs into a dictionary and passes it to `supervisor.process_health_intake()`.
2. `HealthAgent` calculates vitals metrics and calls the LLM for diagnosis.
3. `MonitoringAgent` reads past records from SQLite and detects trends.
4. `NutritionAgent` computes feeding recommendations.
5. `ReportAgent` compiles a unified inspection summary.
6. The record is committed to SQLite memory via `save_health_record()`.
7. Gradio UI updates the status badge, agent boxes, and dropdown choices.

### Q21. How would you add a new agent, such as a Vaccination Agent?
**Answer:** Create `agents/vaccination_agent.py` defining vaccination schedules, instantiate it in `SupervisorAgent`, and call its methods within `process_health_intake()`.

### Q22. What are the limitations of this project?
**Answer:**
- Relies on manual input of vitals (no automated IoT sensors connected yet).
- No computer vision image analysis for skin or wound inspection.
- Educational recommendations only; cannot replace clinical laboratory testing.

### Q23. What future improvements would you propose?
**Answer:**
1. IoT smart-collar integration (BLE/ESP32 temperature sensors).
2. Computer Vision model (YOLOv8) for lesion and gait analysis.
3. Automated WhatsApp/SMS alerts to farmers when status reaches "Critical".
4. Multilingual voice interface for rural farmers.

### Q24. What temperature constitutes a fever in dairy cows?
**Answer:** Normal temperature is 37.8°C to 39.2°C (100°F–102.5°F). Any temperature above 39.5°C is considered a fever, and $>40.0°C$ is a high fever.

### Q25. How does your conversational AI assistant maintain chat context?
**Answer:** The `chat()` method in `SupervisorAgent` receives the history of previous conversation turns `[(user, bot), ...]` and injects the recent turns into the OpenAI API prompt context.

### Q26. Why is prompt engineering important for the agents?
**Answer:** Each agent is given a specific system prompt that restricts its role, prevents it from hallucinating veterinary authority, guides its output structure, and instructs it on when to escalate emergencies.

### Q27. What is temperature parameter in OpenAI API?
**Answer:** Temperature controls response randomness (0 = deterministic and focused, 1 = creative). We use a low temperature (0.3–0.5) for clinical consistency.

### Q28. How do you prevent SQL injection in your SQLite layer?
**Answer:** By using parameterized SQL queries with `?` placeholders instead of raw string formatting.

### Q29. What database tables did you create?
**Answer:** `animals` (master profiles) and `health_records` (time-series transactional checkup logs).

### Q30. How does the system handle missing or invalid user inputs?
**Answer:** Input validation functions in `utils/helpers.py` sanitize numbers, parse comma-separated symptoms, and provide safe default values so the application never crashes.

### Q31. What is the difference between supervised learning and agentic workflows?
**Answer:** Supervised learning trains a static mathematical model to map inputs to outputs. An agentic workflow coordinates dynamic reasoning engines (LLMs) with tools, memory, and multi-step planning to solve open-ended problems.

### Q32. What is the role of pandas in your project?
**Answer:** Pandas is used to convert database dictionaries into structured dataframes for display in Gradio tables and data preparation for Matplotlib charting.

### Q33. Why did you include preset demo buttons?
**Answer:** To enable immediate, 1-click end-to-end demonstration during practical exams and viva presentations without manual typing.

### Q34. How does the system detect recurring symptoms?
**Answer:** The `MonitoringAgent` tokenizes symptoms from current and previous records, computes the set intersection of meaningful keywords, and flags repeated occurrences.

### Q35. How does this project directly satisfy your course syllabus?
**Answer:** It demonstrates all fundamental concepts: Multi-Agent Systems, Supervisor Orchestration, Agent Tools, Persistent Memory, State Tracking, LLM API Integration, and Human-in-the-Loop GUI design.
