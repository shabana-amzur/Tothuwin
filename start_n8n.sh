#!/bin/bash

echo "🚀 Starting n8n..."

# Set environment variables
export N8N_PORT=5678
export N8N_HOST=0.0.0.0

# Start n8n in background
nohup n8n start > n8n.log 2>&1 &

echo "✅ n8n started on http://localhost:5678"
echo "📝 Logs available in n8n.log"
