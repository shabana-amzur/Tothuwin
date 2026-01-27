# Model Selector Integration Guide

## ✅ Implementation Complete

The MCP Style Agent has been successfully integrated into your chatbot with a ChatGPT-style model selector!

## 🎯 Features

### Model Selection Dropdown
- **Location**: Above the chat input box
- **Design**: Similar to ChatGPT's model selector
- **Behavior**: Click to open/close, auto-closes when clicking outside

### Available Models

#### 1. 💬 Gemini (Default)
- **Type**: Standard chat model
- **Features**: RAG support for document queries
- **Best for**: General conversations, document Q&A

#### 2. 🤖 Agent
- **Type**: ReAct pattern agent
- **Tools**: Calculator, Wikipedia search
- **Best for**: Math calculations, factual research
- **Example queries**:
  - "What is 234 * 567?"
  - "Who is Albert Einstein?"
  - "Calculate the area of a circle with radius 5"

#### 3. 🎯 MCP Style Agent
- **Type**: Planner-Selector-Executor-Synthesizer
- **Components**:
  - **Planner**: Breaks queries into actionable steps
  - **Selector**: Validates and selects appropriate tools
  - **Executor**: Runs tools sequentially
  - **Synthesizer**: Combines results into natural responses
- **Tools**: Calculator, Text Analyzer, Search
- **Best for**: Complex multi-step tasks
- **Example queries**:
  - "Calculate 45 * 23 and analyze the result"
  - "Search for quantum computing and analyze the text"
  - "Count words in 'Hello world' and multiply by 5"

## 🧪 How to Test

### Step 1: Access the Application
1. Open browser: http://localhost:3000
2. Login with your credentials

### Step 2: Test Model Selector UI
1. Look above the chat input box
2. Click the model selector button (shows current model)
3. Verify dropdown appears with 3 options
4. Click outside to close dropdown
5. Switch between models and verify selection updates

### Step 3: Test Each Model

#### Test Gemini (Standard Model)
```
Query: "What is the capital of France?"
Expected: Standard conversational response
```

#### Test Agent (ReAct Pattern)
```
Query: "What is 456 * 789?"
Expected: Uses calculator tool, shows thinking process
```

```
Query: "Who invented the telephone?"
Expected: Uses Wikipedia search, provides factual answer
```

#### Test MCP Style Agent
```
Query: "Calculate 123 * 45"
Expected: 
- Planner creates steps
- Selector chooses Calculator tool
- Executor runs calculation
- Synthesizer provides natural response
```

```
Query: "Analyze the text 'Hello world from MCP agent'"
Expected:
- Uses Text Analyzer tool
- Shows word count, character count
- Identifies longest word
```

```
Query: "Search for artificial intelligence"
Expected:
- Uses Search tool (mocked)
- Returns sample results
- Synthesizes findings
```

### Step 4: Test Multi-Step Queries (MCP Style)
```
Query: "Calculate 50 * 20 and then analyze the result"
Expected:
- Step 1: Calculator runs (result: 1000)
- Step 2: Text Analyzer processes "1000"
- Synthesizer combines both results
```

## 🎨 UI Features

### Visual Indicators
- **Selected model**: Highlighted with colored border
  - Gemini: Blue border
  - Agent: Green border
  - MCP Style: Purple border
- **Hover effects**: Gray background on hover
- **Icons**: Emoji icons for each model
- **Descriptions**: Brief description of each model's capabilities

### Responsive Design
- Works on desktop and mobile
- Smooth transitions
- Dark theme consistent with app

## 📊 Backend Logs

Monitor backend logs to see model routing:
```bash
tail -f /tmp/backend.log
```

You should see:
- `Using model: gemini` - Standard Gemini
- `Using agent mode` - ReAct Agent
- MCP Style Agent component outputs (Planner, Executor, etc.)

## 🔧 Implementation Details

### Frontend Changes
**File**: `/frontend/app/page.tsx`

1. **State Management**:
   ```typescript
   const [selectedModel, setSelectedModel] = useState<'gemini' | 'agent' | 'mcp-style'>('gemini');
   const [showModelSelector, setShowModelSelector] = useState(false);
   ```

2. **Model Selector UI**: Dropdown with 3 model options above input

3. **API Call**: Sends `model` parameter to backend
   ```typescript
   body: JSON.stringify({
     message: userMessage.content,
     thread_id: currentThreadId,
     model: selectedModel,
   }),
   ```

### Backend Changes
**File**: `/backend/app/api/chat.py`

Model routing logic:
```python
selected_model = request.model or "gemini"

if selected_model == "mcp-style":
    mcp_response = run_mcp_agent(request.message)
    result = {"message": mcp_response, "model": "MCP Style Agent"}
    
elif selected_model == "agent":
    agent_response = run_basic_agent(request.message)
    result = {"message": agent_response, "model": "Gemini Agent"}
    
else:  # gemini
    # Standard Gemini with RAG support
```

**File**: `/backend/app/models/chat.py`

Added model field to ChatRequest:
```python
model: Optional[str] = Field(
    default="gemini",
    description="Model to use: 'gemini', 'agent', or 'mcp-style'"
)
```

## 🚀 Quick Test Commands

### Start Servers (if not running)
```bash
# Backend
cd backend && nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &

# Frontend
cd frontend && npm run dev
```

### Check Server Status
```bash
# Backend
curl http://localhost:8001/docs

# Frontend
curl http://localhost:3000
```

### Test API Directly
```bash
# Test MCP Style Agent endpoint
curl -X POST http://localhost:8001/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "Calculate 45 * 67",
    "model": "mcp-style"
  }'
```

## 📝 Example Test Scenarios

### Scenario 1: Simple Calculation
1. Select "MCP Style Agent"
2. Type: "What is 789 * 456?"
3. Expected: Planner → Selector → Calculator → Synthesizer → Result: 359784

### Scenario 2: Text Analysis
1. Select "MCP Style Agent"
2. Type: "Analyze this text: 'The quick brown fox jumps over the lazy dog'"
3. Expected: Text Analyzer shows word count, character count, longest word

### Scenario 3: Search Query
1. Select "MCP Style Agent"
2. Type: "Search for machine learning"
3. Expected: Search tool returns results, Synthesizer summarizes

### Scenario 4: Model Comparison
1. Ask same question to all 3 models
2. Query: "What is 456 * 789?"
3. Compare responses:
   - **Gemini**: Direct answer
   - **Agent**: Shows ReAct thinking + Calculator tool
   - **MCP Style**: Shows Planner → Selector → Executor → Synthesizer flow

## 🎓 When to Use Each Model

### Use Gemini When:
- General conversations
- Document Q&A (with uploaded docs)
- Quick responses needed
- No tools required

### Use Agent When:
- Need calculations (complex math)
- Need Wikipedia research
- Want to see reasoning process (ReAct pattern)
- Single-step tool usage

### Use MCP Style Agent When:
- Complex multi-step tasks
- Need multiple tools in sequence
- Want structured problem-solving
- Need to combine different tool outputs
- Want detailed execution logs

## ✅ Verification Checklist

- [ ] Model selector button visible above input
- [ ] Dropdown opens/closes correctly
- [ ] All 3 models listed with icons and descriptions
- [ ] Selected model highlighted
- [ ] Model selection persists during conversation
- [ ] Gemini model works (default behavior)
- [ ] Agent model works (ReAct + tools)
- [ ] MCP Style Agent works (4-component flow)
- [ ] Backend logs show correct model routing
- [ ] UI responsive on mobile

## 🐛 Troubleshooting

### Model selector not showing
- Check browser console for errors
- Verify frontend compiled without errors
- Clear browser cache and refresh

### Model not switching
- Check Network tab in DevTools
- Verify API call sends `model` parameter
- Check backend logs for model routing

### MCP Style Agent not responding
- Check `/tmp/backend.log` for errors
- Verify MCP Style Agent initialized (check startup logs)
- Test MCP endpoint directly: `curl http://localhost:8001/api/mcp/style-agent/info`

### Backend errors
```bash
# View backend logs
tail -f /tmp/backend.log

# Check if backend is running
curl http://localhost:8001/docs
```

## 🎉 Success!

You now have a fully functional model selector integrated into your chatbot, just like ChatGPT! Users can easily switch between:
- Standard Gemini for general chat
- Agent with ReAct pattern for tool-based tasks
- MCP Style Agent for complex multi-step reasoning

Enjoy testing the different models and see how each one handles various types of queries!
