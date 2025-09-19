#!/bin/bash

# TravelBuddy AI Deployment Script for Google Cloud Run
# Usage: ./deploy-script.sh [your-project-id]

set -e  # Exit on any error

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION="us-central1"
BACKEND_SERVICE_NAME="travelbuddy-backend"
FRONTEND_SERVICE_NAME="travelbuddy-frontend"

echo "🚀 Deploying TravelBuddy AI to Google Cloud Run"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Set the project
gcloud config set project $PROJECT_ID

# Build and deploy backend
echo "📦 Building and deploying backend service..."
cd travel_planner_ui/server

# Build the Docker image
gcloud builds submit --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE_NAME .

# Deploy to Cloud Run
gcloud run deploy $BACKEND_SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars ENVIRONMENT=production \
  --port 8080

# Get backend URL
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

echo "✅ Backend deployed at: $BACKEND_URL"

# Build and deploy frontend
echo "📦 Building and deploying frontend service..."
cd ../

# Update environment variables with backend URL
echo "VITE_API_URL=$BACKEND_URL" > .env.production

# Build the Docker image
gcloud builds submit --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE_NAME .

# Deploy to Cloud Run
gcloud run deploy $FRONTEND_SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 1 \
  --max-instances 5 \
  --port 8080

# Get frontend URL
FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME \
  --platform managed \
  --region $REGION \
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