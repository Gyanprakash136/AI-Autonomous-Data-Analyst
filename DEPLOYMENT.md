# Deployment Guide

This guide explains how to deploy the AI Autonomous Data Analyst App using Docker.

## Prerequisites

-   [Docker](https://docs.docker.com/get-docker/) installed on your system.
-   A valid `GOOGLE_API_KEY`.

## Quick Start (Docker Compose)

1.  **Configure Environment**:
    Ensure you have a `.env` file in the root directory with your API key:
    ```
    GOOGLE_API_KEY=your_api_key_here
    ```

2.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```

3.  **Access the App**:
    Open your browser and navigate to `http://localhost:8501`.

## Manual Docker Run

1.  **Build the Image**:
    ```bash
    docker build -t analyst-app .
    ```

2.  **Run the Container**:
    ```bash
    docker run -p 8501:8501 -e GOOGLE_API_KEY=your_api_key_here -v $(pwd)/db:/app/db -v $(pwd)/orchestrator/reports:/app/orchestrator/reports analyst-app
    ```

## Notes

-   **Persistence**: The database (`db/`) and generated reports (`orchestrator/reports/`) are mounted as volumes to persist data even if the container is stopped.
-   **Port**: The app runs on port 8501 by default. You can change the mapping in `docker-compose.yml` (e.g., `"8080:8501"`).

## Google Cloud Run Deployment

This application is stateless (data is loaded from CSV uploads), making it perfect for Google Cloud Run.

### Prerequisites
-   [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) installed and authenticated (`gcloud auth login`).
-   A Google Cloud Project.

### Steps

1.  **Set Project ID**:
    ```bash
    export PROJECT_ID=your-project-id
    gcloud config set project $PROJECT_ID
    ```

2.  **Enable Services**:
    ```bash
    gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
    ```

3.  **Submit Build**:
    This builds the Docker image and stores it in Google Container Registry (GCR) or Artifact Registry.
    ```bash
    gcloud builds submit --tag gcr.io/$PROJECT_ID/analyst-app
    ```

4.  **Deploy to Cloud Run**:
    Replace `YOUR_API_KEY` with your actual Google API Key.
    ```bash
    gcloud run deploy analyst-app \
      --image gcr.io/$PROJECT_ID/analyst-app \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --port 8501 \
      --set-env-vars GOOGLE_API_KEY=YOUR_API_KEY
    ```

5.  **Access**:
    The command will output a Service URL (e.g., `https://analyst-app-xyz-uc.a.run.app`). Click it to use your app!

### Important Note on Persistence
Cloud Run is **stateless**. The SQLite database (`db/analyst.db`) and generated reports will be **reset** if the container restarts or scales down.
-   **Data**: You will need to re-upload your CSV file each time you visit the app after a restart.
-   **Reports**: Download your reports immediately after generation.

