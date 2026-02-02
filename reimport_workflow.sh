#!/bin/bash
# Quick script to reimport n8n workflow

echo "🔄 Reimporting Multi-Agent Workflow"
echo "===================================="
echo ""
echo "Please follow these steps in n8n UI:"
echo ""
echo "1. Open: http://localhost:5678"
echo "2. Go to 'Workflows' in left sidebar"
echo "3. Delete the old 'Multi-Agent AI System' workflow"
echo "4. Click 'Import from File'"
echo "5. Select: $(pwd)/n8n-multi-agent-workflow.json"
echo "6. Activate the workflow (toggle ON)"
echo ""
echo "✅ This will fix the HTTP Request JSON formatting issue"
echo ""
echo "Press Enter when done to test..."
read

echo "Testing..."
curl -X POST http://localhost:5678/webhook/multi-agent \
  -H "Content-Type: application/json" \
  -d '{"message": "What is artificial intelligence?"}' 2>&1 | head -50
