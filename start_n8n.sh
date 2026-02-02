#!/bin/bash

echo "🚀 Starting n8n..."

# Set environment variables
export N8N_PORT=5678
export N8N_HOST=0.0.0.0

# Start n8n in background
nohup n8n start > n8n.log 2>&1 &

echo "✅ n8n started on http://localhost:5678"
echo "📝 Logs available in n8n.log"
echo ""
echo "📋 Next Steps:"
echo "1. Open: http://localhost:5678"
echo "2. Import workflow: n8n-multi-agent-workflow.json"
echo "3. Activate the workflow"
echo "4. Test with: ./test_multi_agent.sh"
