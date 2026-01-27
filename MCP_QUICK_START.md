# MCP (Model Context Protocol) Quick Start

## 🚀 What is MCP?

Model Context Protocol (MCP) is a standardized way to provide structured context and tools to AI agents. Think of it as an API for AI models to access external resources and capabilities in a consistent, discoverable way.

## ⚡ Quick Start

### 1. Start the Servers

```bash
# Backend (port 8001)
cd backend
python -m uvicorn main:app --reload --port 8001

# Frontend (port 3000)
cd frontend
npm run dev
```

### 2. Access MCP Demo

1. Log in to the application at `http://localhost:3000`
2. Click **"🤖 MCP Demo"** button in the sidebar
3. Try the example questions!

## 💡 Try These Examples

### Example 1: Ask About Products
```
Question: "What products does the company offer?"
```
The agent will:
- Access the company knowledge base (MCP Resource)
- Return a list of all 5 products with descriptions

### Example 2: Search Knowledge Base
```
Question: "Search for information about Excel analysis"
```
The agent will:
- Execute the `search_knowledge_base` tool
- Return relevant information from the knowledge base

### Example 3: Get Statistics
```
Question: "Get user statistics for user ID 1"
```
The agent will:
- Execute the `get_user_statistics` tool with user_id=1
- Return comprehensive user activity stats

### Example 4: Calculator
```
Question: "What is 25 * 42 + 100?"
```
The agent will:
- Use the calculator tool
- Return: 25 * 42 + 100 = 1150

### Example 5: Generate Report
```
Question: "Generate a usage report"
```
The agent will:
- Execute the `generate_report` tool
- Return a comprehensive usage report with metrics

## 📚 MCP Components

### Resources (Context)
- **Company Knowledge Base** - Products, policies, services
- **Usage Guidelines** - Best practices for each feature
- **System Status** - Real-time system health

### Tools (Functions)
- **search_knowledge_base** - Search company information
- **get_user_statistics** - Get user activity data
- **generate_report** - Create various reports
- **calculator** - Perform calculations
- **current_datetime** - Get current date/time

## 🔍 Explore the UI

### Chat Tab
- Ask questions to the MCP-enhanced agent
- Click example questions for quick tests
- See how the agent uses MCP resources and tools

### Resources Tab
- Browse available MCP resources
- Click to view resource content
- See what context the agent can access

### Tools Tab
- View all available tools
- See input schemas for each tool
- Understand what tools can do

## 🛠️ API Endpoints

### List Resources
```bash
curl http://localhost:8001/api/mcp/resources \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Chat with Agent
```bash
curl -X POST http://localhost:8001/api/mcp/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What products do we offer?"}'
```

### Execute Tool
```bash
curl -X POST http://localhost:8001/api/mcp/tools/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_knowledge_base",
    "arguments": {"query": "excel"}
  }'
```

## 📖 Learn More

- Full documentation: [MCP_IMPLEMENTATION_GUIDE.md](./MCP_IMPLEMENTATION_GUIDE.md)
- API docs: http://localhost:8001/docs (look for "MCP" tag)
- MCP specification: https://modelcontextprotocol.io/

## 🎯 Key Benefits

1. **Structured Context** - Organized, versioned information
2. **Tool Discovery** - Agents know what they can do
3. **Type Safety** - JSON schemas for all inputs
4. **Modularity** - Easy to add new capabilities
5. **Monitoring** - Track resource/tool usage

## 🤔 Common Questions

**Q: How is MCP different from RAG?**
A: RAG retrieves unstructured documents. MCP provides structured context with schemas and executable tools.

**Q: Can I add my own resources?**
A: Yes! See the implementation guide for how to add custom resources and tools.

**Q: Does the agent always use MCP?**
A: The agent decides based on the question. You can see its reasoning in verbose mode.

**Q: What models support MCP?**
A: MCP is model-agnostic. We're using Google Gemini, but it works with any Langchain-compatible model.

## 🚦 Next Steps

1. ✅ Try all example questions
2. ✅ Explore resources and tools tabs
3. ✅ Read the full implementation guide
4. ✅ Add your own resources/tools
5. ✅ Integrate with your workflows

Happy exploring! 🎉
