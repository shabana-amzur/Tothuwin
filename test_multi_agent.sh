#!/bin/bash
# Multi-Agent System Test Suite
# Comprehensive testing for n8n multi-agent workflow

echo "🧪 Multi-Agent System Test Suite"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
WEBHOOK_URL="http://localhost:5678/webhook/multi-agent"
BACKEND_URL="http://localhost:8001/api/n8n/chat"
API_KEY="n8n-secret-key-12345"

# Test counters
PASSED=0
FAILED=0
TOTAL=0

# Test function
test_agent() {
    local test_name=$1
    local message=$2
    local expected_pattern=$3
    
    echo -e "${BLUE}Test $((TOTAL+1)): $test_name${NC}"
    echo "Message: \"$message\""
    
    result=$(curl -s -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\"}" \
        2>&1)
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ FAILED - Curl error${NC}"
        echo "Error: $result"
        ((FAILED++))
        ((TOTAL++))
        echo ""
        return 1
    fi
    
    if echo "$result" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        echo "Response: $(echo "$result" | jq -r '.message' 2>/dev/null || echo "$result" | head -c 100)"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "Expected pattern: $expected_pattern"
        echo "Got: $(echo "$result" | head -c 200)"
        ((FAILED++))
    fi
    
    ((TOTAL++))
    echo ""
}

# Prerequisite checks
echo "🔍 Prerequisite Checks"
echo "----------------------------------------"

# Check N8N
echo -n "Checking N8N... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5678 | grep -q "200"; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
    echo "Please start N8N with: ./start_n8n.sh"
    exit 1
fi

# Check Backend
echo -n "Checking Backend API... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/n8n/health \
    -H "X-API-Key: $API_KEY" | grep -q "200"; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
    echo "Please start backend with: ./start_backend.sh"
    exit 1
fi

echo ""
echo "========================================"
echo "🎯 Running Agent Tests"
echo "========================================"
echo ""

# Test Suite 1: Coordinator Agent Tests
echo "📋 Test Suite 1: Coordinator Agent (Task Classification)"
echo "----------------------------------------"

test_agent \
    "Simple Calculation" \
    "What is 25 * 48?" \
    "1200"

test_agent \
    "Addition" \
    "Calculate 100 + 250" \
    "350"

test_agent \
    "Division" \
    "What is 1000 / 25?" \
    "40"

test_agent \
    "Subtraction" \
    "Compute 500 - 175" \
    "325"

echo ""
echo "📋 Test Suite 2: Execution Agent (Multiple Tools)"
echo "----------------------------------------"

test_agent \
    "General Chat (Backend API)" \
    "What is artificial intelligence?" \
    "success\|message\|AI"

test_agent \
    "Complex Calculation" \
    "Calculate 12 * 34 * 56" \
    "result"

test_agent \
    "Support Request (MCP Agent)" \
    "Help me calculate 150 * 25" \
    "success\|message"

echo ""
echo "📋 Test Suite 3: Validation Agent"
echo "----------------------------------------"

test_agent \
    "Valid Numeric Result" \
    "What is 999 * 111?" \
    "success"

test_agent \
    "Text Response Validation" \
    "Tell me about Python programming" \
    "success\|message"

echo ""
echo "📋 Test Suite 4: Error Handling"
echo "----------------------------------------"

test_agent \
    "Invalid Math Expression" \
    "Calculate abc * xyz" \
    "success\|error\|message"

test_agent \
    "Edge Case: Division by Zero" \
    "What is 10 / 0?" \
    "success\|error\|Infinity\|message"

echo ""
echo "📋 Test Suite 5: Complex Multi-Step"
echo "----------------------------------------"

test_agent \
    "Multi-step Calculation" \
    "Calculate 100 * 50 and tell me the result" \
    "5000"

test_agent \
    "Reasoning + Calculation" \
    "I need to multiply 25 by 4, can you help?" \
    "100"

echo ""
echo "========================================"
echo "📊 Test Results Summary"
echo "========================================"
echo -e "${BLUE}Total Tests: $TOTAL${NC}"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed! Multi-Agent System is working perfectly.${NC}"
    echo ""
    echo "🔍 You can view detailed execution logs in N8N:"
    echo "   1. Open: http://localhost:5678"
    echo "   2. Click on your workflow"
    echo "   3. Go to 'Executions' tab"
    echo ""
    echo "📊 Metrics to check:"
    echo "   - Average response time"
    echo "   - Agent success rates"
    echo "   - Tool usage statistics"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  Some tests failed. Please review the errors above.${NC}"
    echo ""
    echo "Common Issues:"
    echo "1. Workflow not active in N8N"
    echo "2. Backend API not responding"
    echo "3. Incorrect webhook URL"
    echo "4. API key mismatch"
    echo ""
    echo "Debug Steps:"
    echo "1. Check N8N executions: http://localhost:5678"
    echo "2. Check backend logs: tail -f /tmp/backend_new.log"
    echo "3. Verify workflow is active (green toggle)"
    echo "4. Test backend directly:"
    echo "   curl -X POST http://localhost:8001/api/n8n/chat \\"
    echo "     -H 'X-API-Key: n8n-secret-key-12345' \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"message\":\"test\"}'"
    exit 1
fi
