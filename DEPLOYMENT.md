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

## Google Cloud Run Console Configuration

If you are deploying via the Google Cloud Console UI, use these settings:

1.  **Container image URL**: Select your uploaded image (e.g., `gcr.io/PROJECT_ID/analyst-app`).
2.  **Container name**: You can leave this as default or name it `analyst-app`.
3.  **Container command**: **LEAVE BLANK**. The Dockerfile handles this.
4.  **Container arguments**: **LEAVE BLANK**.
5.  **Variables & Secrets**:
    -   Click **ADD VARIABLE**.
    -   Name: `GOOGLE_API_KEY`
    -   Value: Paste your actual API key (starting with `AIza...`).
6.  **Volume Mounts**: You can skip this. Cloud Run is stateless by default.

## Continuous Deployment from GitHub

To automatically deploy changes whenever you push to GitHub:

1.  Go to the [Google Cloud Run Console](https://console.cloud.google.com/run).
2.  Click **CREATE SERVICE**.
3.  Select **Continuously deploy new revisions from a source repository**.
4.  Click **SET UP WITH CLOUD BUILD**.
5.  **Repository Provider**: Select **GitHub**.
6.  **Repository**: Select your repo (`AI-Autonomous-Data-Analyst`).
    *   *Note: If you don't see it, ensure you renamed it to remove the leading hyphen.*
7.  **Build Configuration**:
    *   Select **Dockerfile**.
    *   Source location: `/` (root).
8.  **Authentication**:
    *   Allow unauthenticated invocations (if you want it public).
9.  **Environment Variables**:
    *   Expand **Container, Networking, Security**.
    *   Go to **Variables & Secrets**.
    *   Add `GOOGLE_API_KEY` and your key value.
10. Click **CREATE**.

Now, every time you `git push origin main`, Google Cloud Build will automatically build the Docker image and deploy it to Cloud Run!

## Railway Deployment

Railway is a great alternative that builds directly from your GitHub repository using the `Dockerfile`.

1.  **Sign Up/Login**: Go to [railway.app](https://railway.app/).
2.  **New Project**: Click **"New Project"** -> **"Deploy from GitHub repo"**.
3.  **Select Repo**: Choose `AI-Autonomous-Data-Analyst`.
4.  **Configuration**:
    *   Railway will automatically detect the `Dockerfile`.
5.  **Variables**:
    *   Click on the new service card.
    *   Go to the **"Variables"** tab.
    *   Add `GOOGLE_API_KEY` with your API key value.
6.  **Deploy**: Railway will automatically build and deploy.
7.  **Public Domain**:
    *   Go to the **"Settings"** tab.
    *   Under "Networking", click **"Generate Domain"** to make your app accessible publicly.

**Note**: You do not need to provide an "image name". Railway builds the image for you from your code.



## Troubleshooting

### "Invalid reference format" Error
If you see an error like `invalid argument ... for "-t, --tag" flag: invalid reference format`, it is likely because your **GitHub repository name starts with a hyphen (-)** (e.g., `-AI-Autonomous-Data-Analyst`).
-   **Cause**: Docker image names cannot start with a hyphen. Google Cloud Build automatically uses your repo name to tag the image.
-   **Fix**: Rename your GitHub repository to remove the leading hyphen (e.g., change `-AI-Autonomous-Data-Analyst` to `AI-Autonomous-Data-Analyst`).



