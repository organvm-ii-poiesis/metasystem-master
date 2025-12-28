#!/bin/bash
set -e

PROJECT_ID="omni-dromenon-engine"
REGION="us-central1"

echo "🚀 Starting Full Deployment for Omni-Dromenon Machina..."

# 1. Landing Page
echo "📦 Building Landing Page..."
docker build --platform linux/amd64 -f Dockerfile.landing-page -t gcr.io/$PROJECT_ID/omni-dromenon-landing:latest .
docker push gcr.io/$PROJECT_ID/omni-dromenon-landing:latest
gcloud run deploy omni-dromenon-landing --image gcr.io/$PROJECT_ID/omni-dromenon-landing:latest --region $REGION --project $PROJECT_ID

# 2. Core Engine
echo "📦 Building Core Engine..."
docker build --platform linux/amd64 -f omni-dromenon-machina/docker/Dockerfile.core-engine -t gcr.io/$PROJECT_ID/omni-dromenon-core:latest omni-dromenon-machina/
docker push gcr.io/$PROJECT_ID/omni-dromenon-core:latest
gcloud run deploy omni-dromenon-core --image gcr.io/$PROJECT_ID/omni-dromenon-core:latest --region $REGION --project $PROJECT_ID

# 3. Performance SDK
echo "📦 Building Performance SDK..."
docker build --platform linux/amd64 --target production -f omni-dromenon-machina/docker/Dockerfile.performance-sdk -t gcr.io/$PROJECT_ID/omni-dromenon-sdk:latest omni-dromenon-machina/
docker push gcr.io/$PROJECT_ID/omni-dromenon-sdk:latest
gcloud run deploy omni-dromenon-sdk --image gcr.io/$PROJECT_ID/omni-dromenon-sdk:latest --region $REGION --project $PROJECT_ID

echo "✅ All services deployed successfully!"
