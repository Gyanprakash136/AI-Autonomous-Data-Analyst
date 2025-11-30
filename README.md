# 🤖 AI Autonomous Data Analyst

A monolithic, production-ready AI application that acts as an autonomous data analyst. It ingests CSV data, performs SQL queries, generates visualizations, provides insights and forecasts, and compiles everything into a PDF report.

## 🚀 Features

-   **Autonomous Analysis**: Converts natural language queries into SQL, executes them, and analyzes the results.
-   **Discovery Mode**: Automatically generates overview charts and recommended questions upon data upload.
-   **Multi-Agent Architecture**:
    -   `SQLAgent`: Generates and cleans SQL queries.
    -   `ChartAgent`: Creates visualizations (Bar, Line, Scatter, Pie).
    -   `InsightAgent`: Provides deep data insights and recommendations.
    -   `ForecastAgent`: Predicts future trends.
    -   `ReportAgent`: Compiles findings into a PDF report.
-   **Robust & Thread-Safe**: Built with a custom `RootOrchestrator` ensuring safe parallel execution of agents.
-   **Deployment Ready**: Dockerized and configured for Google Cloud Run.

## 🛠️ Tech Stack

-   **Frontend**: Streamlit
-   **LLM**: Google Gemini 2.0 Flash Lite (via Google ADK 2025)
-   **Database**: SQLite (In-memory/Local)
-   **Visualization**: Matplotlib
-   **Reporting**: ReportLab

## 🏁 Quick Start

### Prerequisites

-   Python 3.13+
-   Google Cloud API Key

### Local Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Gyanprakash136/-AI-Autonomous-Data-Analyst.git
    cd -AI-Autonomous-Data-Analyst
    ```

2.  **Install Dependencies**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```bash
    GOOGLE_API_KEY=your_api_key_here
    ```

4.  **Run the App**:
    ```bash
    streamlit run ui/app.py
    ```

## 🐳 Docker Deployment

1.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```
2.  **Access**: `http://localhost:8501`

For detailed deployment instructions (including Google Cloud Run), see [DEPLOYMENT.md](DEPLOYMENT.md).

## 🧪 Verification

Run the automated pipeline verification script to ensure everything is working:

```bash
python verify_pipeline.py
```

## 📂 Project Structure

```
.
├── agents/             # AI Agents (SQL, Chart, Insight, etc.)
├── db/                 # SQLite Database
├── orchestrator/       # Pipeline Orchestration logic
├── tools/              # Tools (SQL execution, Chart gen, PDF gen)
├── ui/                 # Streamlit Interface
├── Dockerfile          # Container definition
├── docker-compose.yml  # Local container orchestration
├── main.py             # Entry point (optional)
└── requirements.txt    # Python dependencies
```
