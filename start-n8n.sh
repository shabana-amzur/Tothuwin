#!/bin/bash

echo "🚀 Starting n8n for AI Chat Router..."

# Set environment variables
export N8N_PORT=5678
export N8N_HOST=localhost
export N8N_PROTOCOL=http
export WEBHOOK_URL=http://localhost:5678/

# Start n8n in background
nohup n8n start > n8n.log 2>&1 &

N8N_PID=$!

sleep 5

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 n8n Started Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 n8n Interface: http://localhost:5678"
echo "📋 n8n PID: $N8N_PID"
echo "📄 Logs: n8n.log"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:5678 in your browser"
echo "2. Import the workflow: n8n-workflow-chat-router.json"
echo "3. Activate the workflow"
echo "4. Copy the webhook URL"
echo ""
echo "To stop n8n: kill $N8N_PID"
echo ""
