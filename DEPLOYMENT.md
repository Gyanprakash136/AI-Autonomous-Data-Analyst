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


## Render Deployment

Render is another excellent option that works seamlessly with your Docker setup.

1.  **Sign Up/Login**: Go to [render.com](https://render.com/).
2.  **New Web Service**: Click **"New +"** -> **"Web Service"**.
3.  **Connect GitHub**: Select **"Build and deploy from a Git repository"** and connect your `AI-Autonomous-Data-Analyst` repo.
4.  **Configuration**:
    *   **Runtime**: Select **Docker**.
    *   **Region**: Choose the one closest to you.
    *   **Branch**: `main`.
5.  **Environment Variables**:
    *   Click **"Advanced"** or scroll down to **"Environment Variables"**.
    *   Add Key: `GOOGLE_API_KEY`, Value: `your_api_key_here`.
    *   (Optional) Add Key: `PORT`, Value: `8501` (Render usually detects this, but good to be safe).
6.  **Deploy**: Click **"Create Web Service"**.

Render will build your Docker image and deploy it. It might take a few minutes.





