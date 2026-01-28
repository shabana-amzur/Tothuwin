# Project 14: n8n Workflow Orchestration Integration

## Overview
This integration adds n8n as a lightweight routing/orchestration layer between your chatbot UI and backend agents. **No changes to existing agents or chat logic** - n8n just routes messages intelligently.

## Architecture

```
Chatbot UI (3000)
    ↓
n8n Webhook (5678)
    ↓
Route Logic (n8n)
    ↓
Backend Agent API (8001/api/agent/chat)
    ↓
Existing Agents (unchanged)
```

## What's Been Added

### 1. Backend Endpoint
**File**: `backend/app/api/chat.py`

New endpoint: `POST /api/agent/chat`
- Lightweight wrapper around existing agent logic
- Returns only the response text (no UI logic)
- Used by n8n to call your agents

### 2. n8n Workflow
**File**: `n8n-workflow-chat-router.json`

Routing logic:
- **Support Flow**: If message contains "error", "failed", "issue", "problem", "help" → uses MCP-style agent
- **General Flow**: All other messages → uses standard Gemini agent

### 3. Installation Script
**File**: `start-n8n.sh`
- Starts n8n on port 5678
- Runs in background
- Logs to `n8n.log`

## Setup Instructions

### Step 1: Start n8n

```bash
chmod +x start-n8n.sh
./start-n8n.sh
```

### Step 2: Import Workflow

1. Open http://localhost:5678
2. Create an account (first time only)
3. Click "Workflows" → "Add Workflow"
4. Click "..." menu → "Import from File"
5. Select `n8n-workflow-chat-router.json`
6. Click "Save" and then "Activate"

### Step 3: Get Webhook URL

1. Click on the "Webhook" node in the workflow
2. Click "Execute Node" to get the webhook URL
3. Copy the URL (should be like: `http://localhost:5678/webhook/chat`)

### Step 4: Update Frontend (Next Step)

The webhook URL will be used in the frontend to route messages through n8n.

## How It Works

### Message Flow

1. **User sends message** from chat UI
2. **Frontend calls** n8n webhook with:
   ```json
   {
     "message": "user message",
     "thread_id": 123,
     "user_id": 456,
     "token": "bearer_token"
   }
   ```

3. **n8n routes** based on message content:
   - Contains support keywords → MCP-style agent
   - Normal message → Gemini agent

4. **n8n calls** `/api/agent/chat` with routing decision

5. **Backend processes** using existing agent logic

6. **n8n returns** response to frontend:
   ```json
   {
     "response": "agent response text",
     "model": "model_used",
     "thread_id": 123
   }
   ```

## Testing

### Test Backend Endpoint (Without n8n)

```bash
curl -X POST http://localhost:8001/api/agent/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model": "gemini"
  }'
```

Expected response:
```json
{
  "response": "I'm doing well, thank you! How can I help you today?",
  "model": "gemini-2.5-flash-lite",
  "thread_id": 1,
  "user_id": 1
}
```

### Test n8n Webhook (After Setup)

```bash
curl -X POST http://localhost:5678/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have an error with my code",
    "thread_id": 1,
    "user_id": 1,
    "token": "YOUR_TOKEN"
  }'
```

Should route to Support Agent (MCP-style) because message contains "error".

## Customizing Routes

Edit the workflow in n8n UI:

1. Click on "Route Message" node
2. Add/remove conditions for routing
3. Examples:
   - Route by user type
   - Route by time of day
   - Route by message length
   - Route by sentiment

## Benefits

✅ **No Agent Rewrites**: Existing agents work unchanged
✅ **Simple Integration**: Just one new endpoint
✅ **Flexible Routing**: Easy to add new routes in n8n UI
✅ **Visual Workflows**: See message flow in n8n
✅ **Error Handling**: Fallback responses built-in
✅ **Logging**: All routes logged in n8n

## Troubleshooting

### n8n not starting
```bash
# Check if already running
lsof -ti:5678

# View logs
tail -f n8n.log
```

### Backend endpoint not responding
```bash
# Check backend is running
curl http://localhost:8001/health

# Restart backend
./start_backend.sh
```

### Webhook URL not working
1. Make sure workflow is activated (toggle in n8n UI)
2. Re-execute the Webhook node to get fresh URL
3. Check n8n logs in the UI

## Next Steps

1. ✅ Backend endpoint created
2. ✅ n8n installed and workflow ready
3. ⏳ Update frontend to call n8n webhook (next task)
4. ⏳ Test end-to-end integration

---

**Note**: This is a minimal integration. n8n runs independently and can be stopped/started without affecting your main application. Your existing chatbot functionality remains unchanged.
