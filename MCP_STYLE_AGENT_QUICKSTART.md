# MCP Style Agent - Quick Start Guide

## 🚀 What is the MCP Style Agent?

The **MCP Style Agent** is a modular AI agent system that breaks down complex queries into steps and executes them using specialized tools. It follows the **Planner-Selector-Executor-Synthesizer** pattern.

## ⚡ Quick Start (3 Steps)

### 1. Run the Demo (No API Key Needed)

```bash
cd "/Users/ferozshaik/Desktop/Tothu 3/Tothu"
source venv/bin/activate
python demo_mcp_style_agent.py
```

This demonstrates:
- ✅ Calculator tool (math operations)
- ✅ Text Analyzer tool (word count, readability)
- ✅ Search tool (mocked results)
- ✅ Multi-step plan execution
- ✅ Dependency handling

### 2. Use the API Endpoint

Start the backend if not running:
```bash
cd backend
source ../venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Test with curl:
```bash
curl -X POST "http://localhost:8001/api/mcp/style-agent/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Calculate 25 * 4"}'
```

### 3. Use in Python Code

```python
from app.services.mcp_style_agent import run_mcp_agent

# Simple usage
response = run_mcp_agent("What is 100 + 50?")
print(response)

# Advanced usage
from app.services.mcp_style_agent import MCPStyleAgent

agent = MCPStyleAgent()
response = agent.run("Calculate 25 * 4 and analyze the result")
print(response)
```

## 📝 Example Queries

### Simple Calculations
```
"What is 45 * 67?"
"Calculate 100 + 250"
"What's 1500 divided by 5?"
```

### Text Analysis
```
"Analyze this text: 'The quick brown fox jumps over the lazy dog'"
"Count words in 'Hello World from Python'"
```

### Search
```
"Search for information about Python"
"Find details about LangChain"
```

### Combined Operations
```
"Calculate 25 * 4 and analyze the result"
"Search for Python and count words in the results"
```

## 🏗️ Architecture Overview

```
User Query
    ↓
┌─────────────┐
│  PLANNER    │ → Breaks query into steps
└─────────────┘
    ↓
┌─────────────┐
│TOOL SELECTOR│ → Chooses appropriate tools
└─────────────┘
    ↓
┌─────────────┐
│  EXECUTOR   │ → Runs tools, gathers results
└─────────────┘
    ↓
┌─────────────┐
│SYNTHESIZER  │ → Creates final response
└─────────────┘
    ↓
Final Response
```

## 🛠️ Available Tools

| Tool | Purpose | Example |
|------|---------|---------|
| **Calculator** | Math operations | `calculator("25 * 4")` |
| **Text Analyzer** | Text statistics | `text_analyzer("Hello World")` |
| **Search** | Find information | `search("Python")` |

## 📚 API Endpoints

### Query the Agent
```
POST /api/mcp/style-agent/query
```

Request:
```json
{
  "query": "Calculate 25 * 4 and analyze the result"
}
```

Response:
```json
{
  "success": true,
  "query": "Calculate 25 * 4 and analyze the result",
  "response": "25 multiplied by 4 equals 100. The result..."
}
```

### Get Examples
```
GET /api/mcp/style-agent/examples
```

Returns example queries organized by category.

### Get Architecture Info (No Auth)
```
GET /api/mcp/style-agent/info
```

Returns detailed architecture information.

## 🔍 Viewing the Reasoning Process

The agent logs its internal reasoning. You'll see:

1. **Planning Phase**: Query breakdown into steps
2. **Tool Selection**: Which tools are chosen for each step
3. **Execution**: Tool outputs and results
4. **Synthesis**: How results are combined

Example log output:
```
🎯 PLANNER: Creating execution plan
📋 PLAN CREATED (2 steps):
  Step 1: Calculate 25 * 4 → Tool: calculator
  Step 2: Analyze result → Tool: text_analyzer

⚙️  EXECUTOR: Beginning execution
🔄 Executing Step 1...
🧮 CALCULATOR TOOL: Evaluating '25 * 4'
   ✅ Step 1 completed: 100

🎨 SYNTHESIZER: Creating final response
```

## 🎯 Use Cases

### 1. Mathematical Operations
```python
run_mcp_agent("What's 123 * 456?")
```

### 2. Text Analysis
```python
run_mcp_agent("Analyze this essay for word count and readability")
```

### 3. Information Retrieval
```python
run_mcp_agent("Search for details about Model Context Protocol")
```

### 4. Multi-Step Reasoning
```python
run_mcp_agent(
    "Search for Python, calculate how many letters in 'Python', "
    "and tell me if it's a prime number"
)
```

## 🔧 Adding New Tools

To add a new tool:

1. **Create the tool function** in `AgentTools` class:
```python
@staticmethod
def my_new_tool(input: str) -> Dict[str, Any]:
    # Your tool logic
    return {"result": "..."}
```

2. **Add to ToolType enum**:
```python
class ToolType(Enum):
    MY_NEW_TOOL = "my_new_tool"
```

3. **Register in ToolSelector**:
```python
self.available_tools = {
    ToolType.MY_NEW_TOOL: AgentTools.my_new_tool,
    # ... other tools
}
```

4. **Done!** The Planner will automatically consider it.

## 📖 Documentation

- **Full Guide**: [MCP_STYLE_AGENT_GUIDE.md](MCP_STYLE_AGENT_GUIDE.md)
- **Implementation**: `backend/app/services/mcp_style_agent.py`
- **API Routes**: `backend/app/api/mcp.py`
- **Demo Script**: `demo_mcp_style_agent.py`

## 🆚 MCP Style vs MCP Enhanced

**MCP Style Agent** (this implementation):
- Custom architecture with 4 modular components
- Focus on demonstrating agent patterns
- Standalone tools (calculator, text analyzer, search)
- Educational and extensible

**MCP Enhanced Agent** (existing):
- Integrates with Model Context Protocol
- Uses MCP server resources
- LangChain agent with MCP tools
- Protocol-compliant

## 🎓 Learning Resources

1. Run `python demo_mcp_style_agent.py` to see the pattern in action
2. Read the logs to understand the reasoning process
3. Check `MCP_STYLE_AGENT_GUIDE.md` for deep dive
4. Try the API endpoints with different queries
5. Experiment with adding new tools

## ⚙️ Configuration

The agent uses settings from `backend/.env`:
```bash
GOOGLE_GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3-flash
```

The LLM is used for:
- **Planner**: Breaking queries into steps
- **Synthesizer**: Creating final responses

The tools (calculator, search, text analyzer) work independently.

## 🐛 Troubleshooting

### "API key expired" error
- Update your `GOOGLE_GEMINI_API_KEY` in `backend/.env`
- Use the paid tier API key for production

### Tools not working
- Check tool implementations in `AgentTools` class
- Verify tool is registered in `ToolSelector`

### Plan execution fails
- Check dependency resolution in logs
- Ensure required tools are available

## 🚀 Next Steps

1. ✅ Understand the basic pattern (run demos)
2. ✅ Try example queries via API
3. ✅ Read the full guide for deep understanding
4. ⬜ Add custom tools for your use case
5. ⬜ Integrate with your application
6. ⬜ Build UI to visualize reasoning steps

## 📄 License

Part of the Tothu AI Chat Application project.

---

**Status**: ✅ Fully Functional  
**Pattern**: Planner-Selector-Executor-Synthesizer  
**Built with**: Python, LangChain, Google Gemini, FastAPI
