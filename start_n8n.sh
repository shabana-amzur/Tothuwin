#!/bin/bash

echo "🚀 Starting N8N..."

# Set environment variables
export N8N_BASIC_AUTH_ACTIVE=true
export N8N_BASIC_AUTH_USER=admin
export N8N_BASIC_AUTH_PASSWORD=admin123
export N8N_HOST=localhost
export N8N_PORT=5678
export N8N_PROTOCOL=http

# Start N8N in background
n8n start &

N8N_PID=$!

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 N8N Started Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 N8N Interface: http://localhost:5678"
echo "📋 N8N PID: $N8N_PID"
echo ""
echo "🔐 Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "To stop N8N: kill $N8N_PID"
echo "Or use: pkill -f n8n"
echo ""
