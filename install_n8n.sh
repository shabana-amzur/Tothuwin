#!/bin/bash

echo "🚀 Installing N8N..."
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js first."
    echo "Download from: https://nodejs.org/"
    exit 1
fi

# Install N8N globally
echo "📦 Installing N8N globally..."
npm install -g n8n

# Create N8N directory
mkdir -p ~/.n8n

# Set environment variables
export N8N_BASIC_AUTH_ACTIVE=true
export N8N_BASIC_AUTH_USER=admin
export N8N_BASIC_AUTH_PASSWORD=admin123

echo ""
echo "✅ N8N installed successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Installation Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To start N8N, run:"
echo "  ./start_n8n.sh"
echo ""
echo "Or manually:"
echo "  n8n start --tunnel"
echo ""
echo "N8N will be available at: http://localhost:5678"
echo "Username: admin"
echo "Password: admin123"
echo ""
