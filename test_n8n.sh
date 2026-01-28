#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Testing n8n Integration ===${NC}\n"

# Step 1: Test backend endpoint directly (requires auth token)
echo -e "${BLUE}1. Testing Backend /api/agent/chat endpoint${NC}"
echo "You need to login first to get a token. Skipping direct backend test..."
echo ""

# Step 2: Test n8n webhook (after workflow is activated)
echo -e "${BLUE}2. Testing n8n Webhook${NC}"
echo "Make sure you've:"
echo "  - Imported n8n-workflow-chat-router.json into n8n UI"
echo "  - Activated the workflow"
echo ""

# Test with general message (should route to gemini)
echo -e "${GREEN}Test 1: General message (should route to Gemini)${NC}"
curl -X POST http://localhost:5678/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "userId": 1,
    "threadId": null
  }' | jq '.'

echo -e "\n"

# Test with support message (should route to MCP agent)
echo -e "${GREEN}Test 2: Support message (should route to MCP Agent)${NC}"
curl -X POST http://localhost:5678/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have an error with my code",
    "userId": 1,
    "threadId": null
  }' | jq '.'

echo -e "\n${BLUE}=== Test Complete ===${NC}"
