#!/bin/bash

echo "🛑 Stopping N8N..."

# Find and kill N8N process
pkill -f "n8n start"

if [ $? -eq 0 ]; then
    echo "✅ N8N stopped successfully"
else
    echo "⚠️  N8N was not running or could not be stopped"
fi
