#!/bin/bash

echo "════════════════════════════════════════════════════════"
echo "🎨 Vertex AI Imagen Setup Script"
echo "════════════════════════════════════════════════════════"
echo ""

# Step 1: Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found!"
    echo "   Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✅ gcloud CLI found"
echo ""

# Step 2: Authenticate
echo "📝 STEP 1: Authenticate with Google Cloud"
echo "   This will open your browser..."
echo ""
read -p "Press Enter to authenticate..."
gcloud auth application-default login

echo ""
echo "════════════════════════════════════════════════════════"
echo "📝 STEP 2: Set Your Project"
echo "════════════════════════════════════════════════════════"
echo ""
echo "List of your projects:"
gcloud projects list 2>/dev/null || echo "No projects found. Create one at: https://console.cloud.google.com/"
echo ""
read -p "Enter your PROJECT_ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project ID provided"
    exit 1
fi

# Set the project
gcloud config set project "$PROJECT_ID"

echo ""
echo "════════════════════════════════════════════════════════"
echo "📝 STEP 3: Enable Vertex AI API"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Enabling Vertex AI API..."
gcloud services enable aiplatform.googleapis.com --project="$PROJECT_ID"

echo ""
echo "════════════════════════════════════════════════════════"
echo "📝 STEP 4: Update .env File"
echo "════════════════════════════════════════════════════════"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Add or update GOOGLE_CLOUD_PROJECT
if grep -q "GOOGLE_CLOUD_PROJECT=" .env; then
    # Update existing
    sed -i.bak "s/GOOGLE_CLOUD_PROJECT=.*/GOOGLE_CLOUD_PROJECT=$PROJECT_ID/" .env
    echo "✅ Updated GOOGLE_CLOUD_PROJECT in .env"
else
    # Add new
    echo "" >> .env
    echo "# Google Cloud / Vertex AI Configuration" >> .env
    echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" >> .env
    echo "✅ Added GOOGLE_CLOUD_PROJECT to .env"
fi

# Add or update GOOGLE_CLOUD_LOCATION
if grep -q "GOOGLE_CLOUD_LOCATION=" .env; then
    sed -i.bak "s/GOOGLE_CLOUD_LOCATION=.*/GOOGLE_CLOUD_LOCATION=us-central1/" .env
    echo "✅ Updated GOOGLE_CLOUD_LOCATION in .env"
else
    echo "GOOGLE_CLOUD_LOCATION=us-central1" >> .env
    echo "✅ Added GOOGLE_CLOUD_LOCATION to .env"
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "📝 STEP 5: Restart Backend"
echo "════════════════════════════════════════════════════════"
echo ""
read -p "Restart backend now? (y/n): " RESTART

if [ "$RESTART" = "y" ] || [ "$RESTART" = "Y" ]; then
    echo "🔄 Restarting backend..."
    killall -9 Python 2>/dev/null
    sleep 2
    ./start_backend.sh > /tmp/backend.log 2>&1 &
    sleep 5
    
    echo ""
    echo "✅ Backend restarted!"
    echo ""
    echo "Check logs: tail -f /tmp/backend.log"
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ Setup Complete!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Your configuration:"
echo "  Project: $PROJECT_ID"
echo "  Location: us-central1"
echo ""
echo "Now try: 'generate an image of a futuristic city'"
echo ""
echo "To check if Vertex AI is working:"
echo "  tail -f /tmp/backend.log | grep -i 'imagen\\|vertex'"
echo ""
