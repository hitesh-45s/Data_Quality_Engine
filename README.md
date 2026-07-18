🛡️ Enterprise Data Quality & Profiling Engine

📖 Overview

The Enterprise Data Quality Engine is a scalable, cloud-native microservice built to solve the industry problem of messy, inconsistent data. Instead of relying on manual, error-prone GUI tools, this system provides a fully automated, mathematically rigorous data-cleaning pipeline.

It handles massive datasets in memory, detects anomalies using advanced statistical rules, sanitizes records, and generates an immutable PDF Audit Report for enterprise compliance.

🚀 Live Demo

Frontend Dashboard: https://data-quality-pro.streamlit.app/

Backend API Docs: https://data-quality-api-kitchen.onrender.com/docs

✨ Core Features

🧠 Smart Deduplication: Implements ID-based detection logic to intelligently drop duplicate records while preserving the earliest entry. Falls back to strict row-matching if no ID is present.

📈 Statistical Outlier Detection: Utilizes mathematically sound filters including Z-Score (3 standard deviations) and IQR (Interquartile Range) to automatically isolate and remove impossible numeric anomalies.

🩹 Intelligent Null Imputation: Replaces destructive row-dropping with statistical imputation. Automatically fills missing numeric values using column-specific Means or Medians, and empty text with placeholder constants.

⚙️ Type Casting & Formatting: Strips hidden whitespace from categorical text and strictly standardizes mixed date formats into the ISO 8601 (YYYY-MM-DD) standard.

📑 Automated Compliance Reporting: Dynamically generates a secure, downloadable PDF Audit Report summarizing pre- and post-transformation metrics and system health.

🏗️ System Architecture (Decoupled Microservice)

This project strictly adheres to a decoupled microservice architecture to ensure high availability, security, and independent scaling.

The Frontend (Streamlit): The client-facing dashboard. It provides a secure, corporate-styled SaaS interface, interactive configuration tabs, and real-time metric rendering.

The Backend (FastAPI): An asynchronous REST API. It receives payloads, executes transformation instructions, and securely returns sanitized data without exposing internal logic.

The Engine (Polars): The Rust-based in-memory processing core capable of executing complex matrix operations across large datasets exponentially faster than traditional Pandas scripts.

💻 Local Installation & Setup

If you wish to run this project locally on your machine, follow these steps:

1. Clone the Repository

git clone [https://github.com/your-username/Data_Quality_Engine.git](https://github.com/your-username/Data_Quality_Engine.git)
cd Data_Quality_Engine


2. Install Dependencies

Ensure you have Python 3.10+ installed, then install the required packages:

pip install -r requirements.txt


3. Run the Backend API (FastAPI)

Open a terminal and start the API server:

uvicorn api:app --host 0.0.0.0 --port 8000


The API will be available at http://localhost:8000. You can view the interactive Swagger documentation at http://localhost:8000/docs.

4. Run the Frontend UI (Streamlit)

Open a second terminal window and start the frontend dashboard:

streamlit run app.py


The web interface will automatically open in your browser at http://localhost:8501.

☁️ Cloud Deployment Setup

This project is configured for zero-cost Continuous Integration/Continuous Deployment (CI/CD):

Backend: Deployed via Render web services (linked directly to this GitHub repository).

Frontend: Deployed via Streamlit Community Cloud, bridging via public REST API endpoints.

👨‍💻 Author

Hitesh S, Master of Computer Applications (MCA) Project 
