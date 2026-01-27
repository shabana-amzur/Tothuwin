# 🤖 MCP Style Agent

> A modular AI agent system implementing the Planner-Selector-Executor-Synthesizer pattern

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│   ███╗   ███╗ ██████╗██████╗      █████╗  ██████╗ ███████╗│
│   ████╗ ████║██╔════╝██╔══██╗    ██╔══██╗██╔════╝ ██╔════╝│
│   ██╔████╔██║██║     ██████╔╝    ███████║██║  ███╗█████╗  │
│   ██║╚██╔╝██║██║     ██╔═══╝     ██╔══██║██║   ██║██╔══╝  │
│   ██║ ╚═╝ ██║╚██████╗██║         ██║  ██║╚██████╔╝███████╗│
│   ╚═╝     ╚═╝ ╚═════╝╚═╝         ╚═╝  ╚═╝ ╚═════╝ ╚══════╝│
│                                                            │
│        🎯 Planner  🔧 Selector  ⚙️  Executor  🎨 Synthesizer│
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## 🎯 What is this?

**MCP Style Agent** is an educational implementation of an AI agent that breaks down complex queries into executable steps. It demonstrates clean architecture with four modular components:

1. **🎯 Planner**: Analyzes queries and creates execution plans
2. **🔧 Tool Selector**: Chooses the right tools for each step
3. **⚙️ Executor**: Runs tools and collects results
4. **🎨 Synthesizer**: Combines results into natural responses

## ⚡ Quick Start

### 1️⃣ Run the Demo (No API Key Needed!)

```bash
cd "/Users/ferozshaik/Desktop/Tothu 3/Tothu"
source venv/bin/activate
python demo_mcp_style_agent.py
```

### 2️⃣ Try an Example

```python
from app.services.mcp_style_agent import run_mcp_agent

# Simple calculation
response = run_mcp_agent("What is 100 + 50?")
print(response)
# Output: "100 plus 50 equals 150."

# Text analysis
response = run_mcp_agent("Analyze this text: 'Hello World'")
print(response)
# Output: "The text 'Hello World' contains 2 words..."

# Multi-step
response = run_mcp_agent("Calculate 25 * 4 and analyze the result")
print(response)
# Output: "25 multiplied by 4 equals 100. The result..."
```

### 3️⃣ Use the API

```bash
curl -X POST "http://localhost:8001/api/mcp/style-agent/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Calculate 25 * 4"}'
```

## 🏗️ Architecture

```
                    User asks a question
                            ↓
        ┌───────────────────────────────────────┐
        │  "Calculate 25 * 4 and analyze it"   │
        └────────────────┬──────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │     🎯 PLANNER                         │
        │  ❯ Break into steps                   │
        │  ❯ Identify tools needed               │
        │  ❯ Find dependencies                   │
        └────────────────┬───────────────────────┘
                         │
                         │ Step 1: Calculate 25*4
                         │ Step 2: Analyze result
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │     🔧 TOOL SELECTOR                   │
        │  ❯ Choose Calculator for step 1        │
        │  ❯ Choose Text Analyzer for step 2     │
        │  ❯ Prepare inputs                      │
        └────────────────┬───────────────────────┘
                         │
                         │ Calculator("25*4")
                         │ TextAnalyzer("100")
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │     ⚙️  EXECUTOR                        │
        │  ❯ Run Calculator → 100                │
        │  ❯ Run Text Analyzer → {stats...}      │
        │  ❯ Collect results                     │
        └────────────────┬───────────────────────┘
                         │
                         │ Results: {1: 100, 2: {...}}
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │     🎨 SYNTHESIZER                     │
        │  ❯ Combine all results                 │
        │  ❯ Generate natural response           │
        │  ❯ Format for user                     │
        └────────────────┬───────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │     "25 * 4 = 100. The result..."     │
        └────────────────────────────────────────┘
```

## 🛠️ Built-in Tools

### 🧮 Calculator
Performs safe mathematical operations.
```python
calculator("25 * 4 + 10")
→ {"result": 110, "success": True}
```

### 📝 Text Analyzer
Analyzes text statistics.
```python
text_analyzer("Hello World")
→ {
    "word_count": 2,
    "character_count": 11,
    "longest_word": "Hello",
    "readability": "simple"
}
```

### 🔍 Search
Finds information (mocked).
```python
search("Python programming")
→ {
    "results": [
        {"title": "Python Docs", "snippet": "..."},
        ...
    ]
}
```

## 📝 Example Queries

### Simple Math
```
"What is 45 * 67?"
"Calculate 100 + 250"
```

### Text Analysis
```
"Analyze this text: 'The quick brown fox jumps over the lazy dog'"
"Count words in 'Hello World'"
```

### Combined Operations
```
"Calculate 25 * 4 and analyze the result"
"Search for Python and count words"
"Calculate 100 + 50 then analyze it"
```

## 🔍 See the Reasoning

The agent logs every step of its reasoning:

```
🎬 STARTING MCP AGENT EXECUTION
📥 USER QUERY: Calculate 100 + 50 and analyze the result

🎯 PLANNER: Creating execution plan
📋 PLAN CREATED (2 steps):
  Step 1: Calculate 100 + 50 → Tool: calculator
  Step 2: Analyze result → Tool: text_analyzer (depends on 1)

⚙️  EXECUTOR: Beginning execution
🔄 Executing Step 1: Calculate 100 + 50
🧮 CALCULATOR TOOL: Evaluating '100 + 50'
   ✅ Step 1 completed: 150

🔄 Executing Step 2: Analyze the result
📝 TEXT ANALYZER TOOL: Analyzing '150'
   ✅ Step 2 completed: {word_count: 1, ...}

🎨 SYNTHESIZER: Creating final response
✅ SYNTHESIS COMPLETE

🎉 MCP AGENT EXECUTION COMPLETE
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [MCP_STYLE_AGENT_GUIDE.md](MCP_STYLE_AGENT_GUIDE.md) | 📖 Comprehensive guide (1000+ lines) |
| [MCP_STYLE_AGENT_QUICKSTART.md](MCP_STYLE_AGENT_QUICKSTART.md) | ⚡ Quick reference |
| [MCP_STYLE_AGENT_SUMMARY.md](MCP_STYLE_AGENT_SUMMARY.md) | 📊 Project summary |

## 🎓 Why This Pattern?

### ✅ Modular
Each component is independent and testable.

### ✅ Transparent
See exactly how the agent thinks.

### ✅ Extensible
Add new tools without changing core logic.

### ✅ Educational
Clean code structure with extensive comments.

### ✅ Robust
Error handling at each stage.

## 🔧 Adding Your Own Tool

```python
# 1. Create the tool function
@staticmethod
def my_tool(input: str) -> Dict[str, Any]:
    # Your logic here
    return {"result": "..."}

# 2. Add to ToolType enum
class ToolType(Enum):
    MY_TOOL = "my_tool"

# 3. Register in ToolSelector
self.available_tools = {
    ToolType.MY_TOOL: AgentTools.my_tool,
    ...
}

# Done! The Planner will automatically use it.
```

## 🆚 Comparison

| Feature | MCP Style | Basic Agent | LangChain Agent |
|---------|-----------|-------------|-----------------|
| Modularity | ✅ 4 components | ❌ Monolithic | ⚠️ Framework-dependent |
| Transparency | ✅ Full logging | ⚠️ Limited | ⚠️ Limited |
| Extensibility | ✅ Easy tools | ⚠️ Moderate | ⚠️ Framework-limited |
| Learning | ✅ Educational | ⚠️ Moderate | ⚠️ Complex |

## 📊 Statistics

- **Lines of Code**: ~650 (core agent)
- **Components**: 4 modular classes
- **Tools**: 3 built-in + extensible
- **API Endpoints**: 3 endpoints
- **Documentation**: 1,500+ lines
- **Examples**: 20+ queries
- **Tests**: 6 test cases + 5 demos

## 🚀 Interactive Mode

```bash
python test_mcp_style_agent.py --interactive

🤔 Your query: Calculate 100 * 5 and analyze it
[Agent shows reasoning steps...]
🤖 Agent: 100 multiplied by 5 equals 500...

🤔 Your query: Search for LangChain
[Agent shows reasoning steps...]
🤖 Agent: Found information about LangChain...
```

## 🎯 Use Cases

1. **🧮 Mathematical Operations**: Complex calculations
2. **📝 Text Analysis**: Word counts, readability
3. **🔍 Information Retrieval**: Search and research
4. **🔗 Multi-Step Reasoning**: Combine multiple operations
5. **🎓 Educational**: Learn agent architecture

## 🔐 Configuration

Set in `backend/.env`:
```bash
GOOGLE_GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-3-flash
```

## 📡 API Endpoints

### Query Agent
```
POST /api/mcp/style-agent/query
```

### Get Examples
```
GET /api/mcp/style-agent/examples
```

### Get Info (No Auth)
```
GET /api/mcp/style-agent/info
```

## 🎉 Success Stories

✅ **Demo**: All 5 demos run successfully  
✅ **Tools**: All 3 tools working perfectly  
✅ **Components**: All 4 components tested  
✅ **Dependencies**: Dependency resolution works  
✅ **Logging**: Complete reasoning visibility  
✅ **API**: All endpoints functional  
✅ **Documentation**: Comprehensive guides created

## 🔮 Future Enhancements

- [ ] Parallel execution of independent steps
- [ ] Real search API integration
- [ ] Tool result caching
- [ ] Streaming responses
- [ ] Memory system
- [ ] UI visualization
- [ ] Multi-agent collaboration

## 🤝 Contributing

Want to improve the agent? Here's how:

1. Add new tools to `AgentTools` class
2. Enhance planning prompts
3. Improve error handling
4. Add more comprehensive logging
5. Create visualization tools

## 📖 Learn More

1. Run `python demo_mcp_style_agent.py` to see it in action
2. Read [MCP_STYLE_AGENT_GUIDE.md](MCP_STYLE_AGENT_GUIDE.md) for deep dive
3. Try the API with `curl` or Postman
4. Add your own tools and experiment!

## 🙏 Acknowledgments

Built with:
- **Python** - Programming language
- **LangChain** - LLM framework
- **Google Gemini** - AI model
- **FastAPI** - API framework

## 📄 License

Part of the Tothu AI Chat Application project.

---

<div align="center">

**Status**: ✅ Fully Functional  
**Pattern**: Planner-Selector-Executor-Synthesizer  
**Version**: 1.0.0  
**Date**: January 27, 2026

Made with ❤️ for AI enthusiasts

[📖 Full Guide](MCP_STYLE_AGENT_GUIDE.md) | [⚡ Quick Start](MCP_STYLE_AGENT_QUICKSTART.md) | [📊 Summary](MCP_STYLE_AGENT_SUMMARY.md)

</div>
