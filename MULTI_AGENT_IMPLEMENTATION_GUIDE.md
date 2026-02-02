# 🚀 Multi-Agent System Implementation Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Import Workflow](#import-workflow)
3. [Agent Prompts](#agent-prompts)
4. [Testing](#testing)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

### Prerequisites
- ✅ N8N running on port 5678
- ✅ Backend API running on port 8001
- ✅ N8N credentials configured

### 5-Minute Setup
```bash
# 1. Open N8N
open http://localhost:5678

# 2. Navigate to: Workflows → Import from File

# 3. Select: n8n-multi-agent-workflow.json

# 4. Activate the workflow

# 5. Test the webhook
curl -X POST http://localhost:5678/webhook/multi-agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Calculate 25 * 48"}'
```

---

## 📥 Import Workflow

### Step-by-Step Import

1. **Open N8N Dashboard**
   - URL: http://localhost:5678
   - Login with your credentials

2. **Create New Workflow**
   - Click "Workflows" in sidebar
   - Click "+ Add Workflow"

3. **Import JSON**
   - Click the "..." menu (top right)
   - Select "Import from File"
   - Choose `n8n-multi-agent-workflow.json`
   - Click "Import"

4. **Configure Credentials**
   - Click on "Backend API" node
   - Add header: `X-API-Key: n8n-secret-key-12345`
   - Save

5. **Activate Workflow**
   - Toggle "Active" switch (top right)
   - Workflow is now live!

6. **Get Webhook URL**
   - Click on "Webhook Entry Point" node
   - Copy URL: `http://localhost:5678/webhook/multi-agent`
   - Save this URL for testing

---

## 🧠 Agent Prompts & Logic

### Coordinator Agent Prompt
```javascript
// SYSTEM PROMPT
You are a Coordinator Agent in a multi-agent system.
Your role is to analyze user requests and determine:
1. Task Type (calculation, api_call, data_query, general_chat, support)
2. Required Tools (calculator, http_request, database, backend_api)
3. Complexity Level (low, medium, high)
4. Execution Plan (step-by-step actions)

Classification Rules:
- "calculate X" → calculation (use calculator)
- "get/fetch data" → api_call (use http_request)
- "search/find" → data_query (use database)
- "help/error/issue" → support (use mcp_agent)
- General questions → general_chat (use gemini)

Output Format:
{
  "task_type": "calculation|api_call|data_query|general_chat|support",
  "confidence": 0.0-1.0,
  "tools_required": ["tool1", "tool2"],
  "complexity": "low|medium|high",
  "reasoning": "explanation",
  "execution_plan": [
    {"step": 1, "action": "action_name", "tool": "tool_name"}
  ]
}
```

### Execution Agent Prompt
```javascript
// SYSTEM PROMPT
You are an Execution Agent.
Your role is to perform actions using the assigned tools.

Available Tools:
1. Calculator - mathematical operations
2. HTTP Request - API calls
3. Database - data queries
4. Backend API - AI model calls

Execution Process:
1. Receive task from Coordinator
2. Validate inputs
3. Execute using appropriate tool
4. Capture result and errors
5. Log execution time
6. Return structured output

Output Format:
{
  "status": "success|failed",
  "result": "actual_result",
  "tool_used": "tool_name",
  "execution_time_ms": 123,
  "intermediate_steps": [],
  "errors": []
}
```

### Validation Agent Prompt
```javascript
// SYSTEM PROMPT
You are a Validation Agent.
Your role is to verify output quality and correctness.

Validation Checks:
1. Completeness - all required fields present
2. Correctness - data types match expectations
3. Format - proper structure
4. Logical Consistency - result makes sense
5. Error Detection - identify issues

Scoring:
- 0.9-1.0: Excellent - approve immediately
- 0.75-0.89: Good - approve with notes
- 0.5-0.74: Fair - recommend retry
- 0.0-0.49: Poor - reject

Output Format:
{
  "is_valid": true|false,
  "confidence_score": 0.0-1.0,
  "validation_checks": {
    "completeness": "passed|failed",
    "correctness": "passed|failed",
    "format": "passed|failed"
  },
  "issues_found": [],
  "recommendation": "approve|retry|reject"
}
```

---

## 🧪 Testing the Multi-Agent System

### Test Case 1: Simple Calculation
```bash
curl -X POST http://localhost:5678/webhook/multi-agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is 25 * 48?"
  }'
```

**Expected Flow:**
1. ✅ Coordinator identifies as "calculation"
2. ✅ Execution uses calculator tool → 1200
3. ✅ Validation checks result → valid
4. ✅ Response: "The result of 25 * 48 is **1200**"

**Expected Response:**
```json
{
  "success": true,
  "message": "The result of 25 * 48 is **1200**",
  "details": {
    "expression": "25 * 48",
    "result": 1200,
    "method": "calculator"
  },
  "metadata": {
    "request_id": "20260201120000-abc",
    "task_type": "calculation",
    "confidence": 0.95,
    "validation_score": 1.0,
    "tools_used": ["calculator"],
    "processing_time_ms": 45
  },
  "agents_involved": [
    {"name": "coordinator", "role": "task_routing"},
    {"name": "execution", "role": "action_performance"},
    {"name": "validation", "role": "quality_assurance"}
  ]
}
```

---

### Test Case 2: API Call (Backend)
```bash
curl -X POST http://localhost:5678/webhook/multi-agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is artificial intelligence?"
  }'
```

**Expected Flow:**
1. ✅ Coordinator identifies as "general_chat"
2. ✅ Execution calls backend API with Gemini
3. ✅ Validation checks response → valid
4. ✅ Response: AI explanation

---

### Test Case 3: Support Request
```bash
curl -X POST http://localhost:5678/webhook/multi-agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me calculate 150 * 25"
  }'
```

**Expected Flow:**
1. ✅ Coordinator identifies as "support" (keyword: help)
2. ✅ Execution calls backend API with MCP agent
3. ✅ Validation checks response → valid
4. ✅ Response: MCP agent's detailed response

---

### Test Case 4: Complex Multi-Step
```bash
curl -X POST http://localhost:5678/webhook/multi-agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate 100 * 50 and tell me if it is even"
  }'
```

**Expected Flow:**
1. ✅ Coordinator creates multi-step plan
2. ✅ Execution performs calculation
3. ✅ Execution checks if even
4. ✅ Validation verifies logic
5. ✅ Response: "100 × 50 = 5000, which is an even number"

---

## 🎨 Node-by-Node Explanation

### 1. Webhook Entry Point
**Purpose**: Receives incoming requests
**Configuration**:
- Method: POST
- Path: `/multi-agent`
- Response Mode: Using Webhook Response Node

### 2. Initialize Context
**Purpose**: Sets up workflow context
**Data Created**:
- `request_id`: Unique identifier
- `user_input`: User's message
- `timestamp`: Request time
- `workflow_state`: Current state

### 3. Coordinator Agent (Code Node)
**Purpose**: Task classification and routing
**Logic**:
- Pattern matching on user input
- Task type determination
- Tool selection
- Execution plan creation

**Key Functions**:
```javascript
classifyTask(input) // Returns task classification
extractNumbers(input) // Finds numbers in text
extractOperator(input) // Identifies math operators
```

### 4. Route Decision (IF Node)
**Purpose**: Branches workflow based on task type
**Conditions**:
- TRUE: calculation → Calculator tool
- FALSE: other types → Backend API

### 5. Execution Agent - Calculator
**Purpose**: Performs mathematical calculations
**Logic**:
- Parses numbers and operators
- Executes calculation
- Handles division by zero
- Returns structured result

### 6. Execution Agent - Backend API
**Purpose**: Calls backend AI models
**Configuration**:
- URL: `http://localhost:8001/api/n8n/chat`
- Headers: `X-API-Key: n8n-secret-key-12345`
- Body: message, model, user_email

### 7. Validation Agent (Code Node)
**Purpose**: Quality assurance
**Validation Types**:
- Calculation validation (numeric, finite, complete)
- API validation (response exists, format correct)

**Scoring System**:
```javascript
score = passed_checks / total_checks
is_valid = score >= 0.75
recommendation = is_valid ? 'approve' : score >= 0.5 ? 'retry' : 'reject'
```

### 8. Validation Check (IF Node)
**Purpose**: Route to success or error path
**Conditions**:
- TRUE: is_valid → Success path
- FALSE: not valid → Error path

### 9. Response Formatter (Code Node)
**Purpose**: Creates human-readable response
**Functions**:
- `formatCalculationResponse()` - Math results
- `formatAPIResponse()` - Text responses
- Adds metadata and agent info

### 10. Error Handler (Code Node)
**Purpose**: Graceful error handling
**Output**:
- User-friendly error message
- Validation issues
- Retry recommendation

### 11. Webhook Response Nodes
**Purpose**: Returns result to client
**Types**:
- Success response (200 OK)
- Error response (with retry info)

### 12. Logger (Set Node)
**Purpose**: Logs workflow execution
**Data Logged**:
- Request ID
- Status (success/failed)
- Timestamp
- Can be extended to database

---

## 🔧 Advanced Features

### Feature 1: Memory / State Management

**Add a Database Node**:
```javascript
// Store conversation history
{
  "request_id": "uuid",
  "user_input": "message",
  "response": "agent response",
  "timestamp": "2026-02-01T10:00:00Z"
}
```

**Configuration**:
1. Add "Postgres" or "MySQL" node after Logger
2. Store: request_id, user_input, response, timestamp
3. Query history before Coordinator for context

---

### Feature 2: Confidence Scoring

**Enhanced Coordinator Agent**:
```javascript
// Add confidence calculation
function calculateConfidence(patterns, input) {
  let score = 0.5; // baseline
  
  // Exact keyword match: +0.3
  if (exactMatch) score += 0.3;
  
  // Pattern match: +0.2
  if (patternMatch) score += 0.2;
  
  // Number extraction success: +0.15
  if (numbersFound) score += 0.15;
  
  return Math.min(score, 1.0);
}
```

---

### Feature 3: Human-in-the-Loop

**Add Approval Step**:
1. After Execution, before Validation
2. Send notification (Email/Slack)
3. Wait for approval
4. Continue or abort

**Implementation**:
```javascript
// Add "Wait" node
{
  "type": "webhook",
  "path": "approve/:request_id",
  "action": "resume_workflow"
}
```

---

### Feature 4: Retry Logic

**Enhanced Error Handler**:
```javascript
// Check retry count
const retryCount = $json.retry_count || 0;
const maxRetries = 3;

if (retryCount < maxRetries) {
  // Loop back to Execution Agent
  return {
    ...data,
    retry_count: retryCount + 1,
    retry_timestamp: new Date().toISOString()
  };
} else {
  // Give up, return error
  return errorResponse;
}
```

---

### Feature 5: Rate Limiting

**Add Function Node Before Execution**:
```javascript
// Check request rate
const requestsPerMinute = 10;
const now = Date.now();
const window = 60000; // 1 minute

// Get recent requests from memory
const recentRequests = $static.requests || [];
const activeRequests = recentRequests.filter(
  t => now - t < window
);

if (activeRequests.length >= requestsPerMinute) {
  throw new Error('Rate limit exceeded');
}

// Store this request
$static.requests = [...activeRequests, now];
```

---

## 📊 Monitoring & Analytics

### Key Metrics to Track

1. **Performance Metrics**
   ```javascript
   {
     "avg_response_time_ms": 500,
     "p95_response_time_ms": 1200,
     "p99_response_time_ms": 2000
   }
   ```

2. **Success Rates**
   ```javascript
   {
     "total_requests": 1000,
     "successful": 950,
     "failed": 50,
     "success_rate": 0.95
   }
   ```

3. **Agent Performance**
   ```javascript
   {
     "coordinator": { "calls": 1000, "avg_time_ms": 50 },
     "execution": { "calls": 1000, "avg_time_ms": 300 },
     "validation": { "calls": 1000, "avg_time_ms": 100 }
   }
   ```

4. **Tool Usage**
   ```javascript
   {
     "calculator": 400,
     "backend_api": 550,
     "database": 50
   }
   ```

---

## 🐛 Troubleshooting

### Issue 1: Webhook Not Found
**Error**: `404 Not Found`
**Solution**:
1. Check workflow is "Active"
2. Verify webhook path: `/webhook/multi-agent`
3. Restart n8n if needed

### Issue 2: Backend API Connection Failed
**Error**: `ECONNREFUSED`
**Solution**:
```bash
# Check backend is running
curl http://localhost:8001/api/n8n/health \
  -H "X-API-Key: n8n-secret-key-12345"

# Restart if needed
./start_backend.sh
```

### Issue 3: Validation Always Fails
**Error**: Low confidence scores
**Solution**:
1. Check validation thresholds (currently 0.75)
2. Review validation logic
3. Add debug logging

### Issue 4: Slow Response Times
**Solution**:
1. Check backend API performance
2. Add caching for common requests
3. Optimize agent logic
4. Use parallel execution where possible

---

## 🚀 Production Deployment

### Checklist
- [ ] Environment variables configured
- [ ] API keys secured
- [ ] Error handling tested
- [ ] Retry logic verified
- [ ] Monitoring enabled
- [ ] Rate limiting configured
- [ ] Logging implemented
- [ ] Documentation updated
- [ ] Load testing completed
- [ ] Backup strategy in place

### Environment Variables
```bash
# Add to .env
N8N_WEBHOOK_URL=http://localhost:5678/webhook/multi-agent
N8N_API_KEY=n8n-secret-key-12345
BACKEND_API_URL=http://localhost:8001
MAX_RETRIES=3
VALIDATION_THRESHOLD=0.75
REQUEST_TIMEOUT_MS=30000
```

---

## 📚 Additional Resources

- N8N Documentation: https://docs.n8n.io
- Backend API Docs: http://localhost:8001/docs
- Multi-Agent Architecture: MULTI_AGENT_ARCHITECTURE.md

---

## 🎯 Next Steps

1. ✅ Import workflow into n8n
2. ✅ Test with sample requests
3. ✅ Monitor execution logs
4. ✅ Customize agent logic for your use case
5. ✅ Add advanced features (memory, approval)
6. ✅ Deploy to production

**You now have a production-ready multi-agent system! 🎉**
