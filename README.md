# 💬 Application Usage Pulse

This repository supports an internal LLM-powered tool that converts natural language prompts into SQL queries. It includes an analytics pipeline to monitor usage patterns, track team-wise adoption, and extract actionable feedback to support internal product growth and commercialization.

---
Please ensure that your service account credentials file is included before running the script, and make sure it also contains the PostgreSQL connection details.
---

## 🔧 Key Features

- 🔐 **Secure Access via Google Authenticator**  
  Tracks authenticated usage of the Streamlit-based LLM tool with user-level metadata.

- 📊 **Usage & Feedback Analytics**  
  - Captures session data (user ID, prompt, timestamp, frequency)
  - Logs sentiment and feedback via feedback forms and usage tags

- ⚙️ **Automated Data Pipeline**  
  - Stores logs in **AWS PostgreSQL**  
  - Schedules extraction jobs via cron  
  - ETL pipeline built in **Python**

- 🧠 **Insightful Dashboard in Tableau**  
  - Tracks usage trends by team  
  - Shows top prompt types, session volume, sentiment over time  
  - Highlights keywords from negative feedback using NLP preprocessing
