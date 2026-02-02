#!/bin/bash
# Test N8N model from frontend perspective

echo "🧪 Testing N8N Model Integration"
echo "=================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Wait for backend
echo -n "Waiting for backend... "
for i in {1..10}; do
  if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ready${NC}"
    break
  fi
  sleep 1
  if [ $i -eq 10 ]; then
    echo -e "${RED}❌ Backend not responding${NC}"
    exit 1
  fi
done

# Login to get auth token
echo -n "Getting auth token... "
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}' | jq -r '.access_token')

if [ "$TOKEN" != "null" ] && [ ! -z "$TOKEN" ]; then
  echo -e "${GREEN}✅ Done${NC}"
else
  echo -e "${RED}❌ Failed to get token${NC}"
  exit 1
fi

# Test N8N model via chat endpoint
echo -e "\n${BLUE}Test 1: Calculation via N8N model${NC}"
echo "Message: What is 15 * 20?"

response=$(curl -s -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "What is 15 * 20?",
    "model": "n8n"
  }' 2>&1)

if echo "$response" | grep -q "300"; then
  echo -e "${GREEN}✅ PASSED${NC}"
  echo "Response: $(echo "$response" | jq -r '.message' 2>/dev/null || echo "$response" | head -c 150)"
else
  echo -e "${RED}❌ FAILED${NC}"
  echo "Response: $response"
fi

echo -e "\n${BLUE}Test 2: General chat via N8N model${NC}"
echo "Message: What is artificial intelligence?"

response=$(curl -s -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "message": "What is artificial intelligence?",
    "model": "n8n"
  }' 2>&1)

if echo "$response" | grep -qi "intelligence"; then
  echo -e "${GREEN}✅ PASSED${NC}"
  echo "Response: $(echo "$response" | jq -r '.message' 2>/dev/null || echo "$response" | head -c 150)"
else
  echo -e "${RED}❌ FAILED${NC}"
  echo "Response: $response"
fi

echo -e "\n=================================="
echo "✅ N8N model integration test complete!"
echo "You can now select '🔄 N8N Multi-Agent' in the frontend."
