#!/bin/bash

# TravelBuddy AI Deployment Script for Google Cloud Run
# Usage: ./deploy-script.sh [your-project-id]

set -euo pipefail  # Exit on error, undefined var, or pipefail

# Configuration
PROJECT_ID=${1:-}
REGION="us-central1"
BACKEND_SERVICE_NAME="travelbuddy-backend"
FRONTEND_SERVICE_NAME="travelbuddy-frontend"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "Usage: $0 <gcp-project-id>"
  exit 1
fi

echo "🚀 Deploying TravelBuddy AI to Google Cloud Run"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set the project
gcloud config set project "$PROJECT_ID"

# Build and deploy backend
echo "📦 Building and deploying backend service..."

# Build the Docker image (use repo root as context; Dockerfile references repo paths)
gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE_NAME \
  --file travel_planner_ui/server/Dockerfile \
  .

# Deploy to Cloud Run
gcloud run deploy "$BACKEND_SERVICE_NAME" \
  --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE_NAME \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars ENVIRONMENT=production,GOOGLE_API_KEY=${GOOGLE_API_KEY:-},GEMINI_API_KEY=${GEMINI_API_KEY:-},SERP_API_KEY=${SERP_API_KEY:-} \
  --port 8080

# Get backend URL
BACKEND_URL=$(gcloud run services describe "$BACKEND_SERVICE_NAME" \
  --platform managed \
  --region "$REGION" \
  --format 'value(status.url)')

echo "✅ Backend deployed at: $BACKEND_URL"

# Build and deploy frontend
echo "📦 Building and deploying frontend service..."

# Create/update env file used by Vite build
echo "VITE_API_URL=$BACKEND_URL" > travel_planner_ui/.env.production

# Build the Docker image for frontend (use UI folder as context)
gcloud builds submit \
  --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE_NAME \
  --file travel_planner_ui/Dockerfile \
  travel_planner_ui

# Deploy to Cloud Run
gcloud run deploy "$FRONTEND_SERVICE_NAME" \
  --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE_NAME \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 1 \
  --max-instances 5 \
  --port 8080

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe "$FRONTEND_SERVICE_NAME" \
  --platform managed \
  --region "$REGION" \
  --format 'value(status.url)')

echo "✅ Frontend deployed at: $FRONTEND_URL"

echo ""
echo "🎉 Deployment Complete!"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo "📋 Next Steps:"
echo "1. Update your API keys in Google Secret Manager"
echo "2. Configure custom domain (optional)"
echo "3. Set up monitoring and logging"
