# Model Context Protocol (MCP) Implementation

## 🎯 Overview

This implementation demonstrates how to integrate **Model Context Protocol (MCP)** with a Langchain agent. MCP is a standardized protocol for providing structured context and tools to AI models, enabling more intelligent and context-aware responses.

## 🏗️ Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MCP Agent      │ ◄──── Langchain Agent
│  (mcp_agent.py) │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────┐   ┌──────┐
│ MCP │   │ MCP  │
│Tools│   │Resources│
└─────┘   └──────┘
    │         │
    └────┬────┘
         ▼
┌─────────────────┐
│  MCP Server     │
│(mcp_server.py)  │
└─────────────────┘
```

## 📁 File Structure

```
backend/
├── app/
│   ├── api/
│   │   └── mcp.py              # MCP API endpoints
│   └── services/
│       ├── mcp_server.py       # MCP server implementation
│       └── mcp_agent.py        # MCP-enhanced Langchain agent
```

## 🔧 Components

### 1. MCP Server (`mcp_server.py`)

The MCP server provides:

#### **Resources** (Structured Context)
- `context://company/knowledge-base` - Company products, policies, services
- `context://company/guidelines` - Usage guidelines and best practices
- `context://system/status` - System health and status

#### **Tools** (Executable Functions)
- `get_user_statistics` - Get user activity stats
- `search_knowledge_base` - Search company knowledge base
- `generate_report` - Generate various types of reports

### 2. MCP Agent (`mcp_agent.py`)

Langchain agent enhanced with:
- Access to all MCP resources
- Ability to execute MCP tools
- Standard tools (calculator, datetime)
- Context-aware responses

### 3. API Endpoints (`mcp.py`)

RESTful API for MCP functionality:
- `GET /api/mcp/resources` - List all resources
- `GET /api/mcp/resources/{uri}` - Get specific resource
- `GET /api/mcp/tools` - List all tools
- `POST /api/mcp/tools/execute` - Execute a tool
- `POST /api/mcp/chat` - Chat with MCP agent
- `GET /api/mcp/demo` - Get demo examples
- `GET /api/mcp/status` - Get MCP status

## 🚀 Usage Examples

### Example 1: Chat with MCP Agent

**Request:**
```bash
curl -X POST http://localhost:8001/api/mcp/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What products does the company offer?",
    "use_mcp": true
  }'
```

**Response:**
```json
{
  "success": true,
  "question": "What products does the company offer?",
  "answer": "Based on the company knowledge base, we offer 5 main products:\n\n1. **AI Chat Assistant** - Powered by Google Gemini...",
  "mcp_enabled": true,
  "agent_type": "mcp_enhanced"
}
```

### Example 2: Access MCP Resource

**Request:**
```bash
curl -X GET "http://localhost:8001/api/mcp/resources/context://company/knowledge-base" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "resource": {
    "uri": "context://company/knowledge-base",
    "name": "Company Knowledge Base",
    "description": "Information about company products, policies, and services",
    "mimeType": "text/plain",
    "content": "# Company Information\n\n## Products:\n..."
  }
}
```

### Example 3: Execute MCP Tool

**Request:**
```bash
curl -X POST http://localhost:8001/api/mcp/tools/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_knowledge_base",
    "arguments": {
      "query": "excel",
      "category": "products"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "query": "excel",
  "category": "products",
  "results": [
    {
      "resource": "Company Knowledge Base",
      "uri": "context://company/knowledge-base",
      "description": "Information about company products...",
      "relevance": "high"
    }
  ],
  "count": 1
}
```

### Example 4: List Available Resources

**Request:**
```bash
curl -X GET http://localhost:8001/api/mcp/resources \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "resources": [
    {
      "uri": "context://company/knowledge-base",
      "name": "Company Knowledge Base",
      "description": "Information about company products, policies, and services"
    },
    {
      "uri": "context://company/guidelines",
      "name": "Usage Guidelines",
      "description": "Best practices and usage guidelines"
    },
    {
      "uri": "context://system/status",
      "name": "System Status",
      "description": "Current system status and health metrics"
    }
  ]
}
```

## 🎮 Interactive Demo

Visit the demo endpoint for interactive examples:

```bash
curl -X GET http://localhost:8001/api/mcp/demo \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This returns comprehensive examples organized by category:
- **Resource Access** - How to query MCP resources
- **Tool Execution** - How to use MCP tools
- **Combined Capabilities** - Using multiple MCP features together

## 🧪 Testing MCP Agent

### Test 1: Product Information
```
Question: "What products does the company offer?"
Expected: Agent accesses company knowledge base and lists all 5 products
```

### Test 2: Usage Guidelines
```
Question: "How do I use Excel analysis?"
Expected: Agent retrieves Excel-specific guidelines from MCP resources
```

### Test 3: Search Knowledge Base
```
Question: "Search for information about SQL queries"
Expected: Agent uses search_knowledge_base tool and returns relevant results
```

### Test 4: User Statistics
```
Question: "Get statistics for user ID 1"
Expected: Agent executes get_user_statistics tool with user_id=1
```

### Test 5: Mathematical Operations
```
Question: "Calculate 42 * 15 + 100"
Expected: Agent uses calculator tool: 42 * 15 + 100 = 730
```

### Test 6: Combined Query
```
Question: "What products do we have and how many users are active?"
Expected: Agent combines knowledge base resource + user statistics tool
```

## 🔐 Authentication

All MCP endpoints require authentication:

```python
from app.utils.auth import get_current_active_user

current_user: User = Depends(get_current_active_user)
```

## 📊 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

Look for the **MCP** tag to see all MCP endpoints.

## 🛠️ Extending MCP

### Adding New Resources

```python
# In mcp_server.py
new_resource = MCPResource(
    uri="context://custom/resource",
    name="Custom Resource",
    description="My custom resource"
)
new_resource.content = "Resource content here"
self.resources.append(new_resource)
```

### Adding New Tools

```python
# In mcp_server.py
new_tool = MCPTool(
    name="my_custom_tool",
    description="Description of what it does",
    input_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
)
self.tools.append(new_tool)

# Implement the tool function
def _my_custom_tool(self, param1: str) -> Dict[str, Any]:
    # Tool implementation
    return {"result": "success"}
```

### Integrating with Langchain Agent

```python
# In mcp_agent.py
tools.append(Tool(
    name="my_tool",
    description="Tool description for agent",
    func=lambda x: self._execute_mcp_tool("my_custom_tool", {"param1": x})
))
```

## 🎯 Benefits of MCP

1. **Structured Context** - Organized, versioned context instead of raw prompts
2. **Tool Standardization** - Consistent interface for external functions
3. **Modularity** - Easy to add/remove resources and tools
4. **Discoverability** - Agents can list available capabilities
5. **Type Safety** - JSON schemas for tool inputs
6. **Reusability** - Same MCP server for multiple agents
7. **Monitoring** - Track which resources/tools are used

## 🔄 MCP Protocol Flow

```
1. Agent receives user query
2. Agent lists available MCP resources
3. Agent determines which resources/tools to use
4. Agent executes MCP tools or accesses resources
5. MCP server returns structured data
6. Agent synthesizes response
7. User receives context-aware answer
```

## 📈 Performance

- **Resource Access**: ~10ms (in-memory)
- **Tool Execution**: ~50-100ms (depending on complexity)
- **Agent Invocation**: ~2-5s (includes LLM call)

## 🔍 Debugging

Enable verbose logging:

```python
# In mcp_agent.py
agent_executor = AgentExecutor(
    agent=agent,
    tools=self.tools,
    verbose=True,  # Shows agent's thought process
    handle_parsing_errors=True
)
```

## 🌟 Best Practices

1. **Resource Organization** - Group related context together
2. **Tool Granularity** - One tool, one responsibility
3. **Schema Validation** - Use strict JSON schemas for tools
4. **Error Handling** - Graceful degradation if tools fail
5. **Caching** - Cache expensive resource computations
6. **Versioning** - Version your MCP resources for compatibility

## 🚦 Status Codes

- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (missing/invalid token)
- `404` - Resource/tool not found
- `500` - Server error

## 📝 Example Integration

```python
from app.services.mcp_agent import MCPEnhancedAgent

# Initialize agent
agent = MCPEnhancedAgent(gemini_api_key)

# Simple query
response = agent.invoke("What products do we offer?")

# Query with context
response = agent.invoke(
    "Compare our SQL and Excel features",
    chat_history=[{"role": "user", "content": "Previous question..."}]
)

# Get available capabilities
resources = agent.get_available_resources()
tools = agent.get_available_tools()
```

## 🎓 Learn More

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Langchain Documentation](https://python.langchain.com/)
- [Google Gemini API](https://ai.google.dev/)

## 📞 Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review example requests in `/api/mcp/demo`
3. Enable verbose logging for debugging
