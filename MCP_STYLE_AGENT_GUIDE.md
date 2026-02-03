# MCP Style Agent - Complete Implementation Guide

## 🎯 Overview

This document describes the **MCP Style Agent** - a modular AI agent system built with the **Planner-Selector-Executor-Validator-Synthesizer** pattern (5-component architecture). This is a clean, educational implementation that demonstrates how to build sophisticated AI agents with clear separation of concerns and built-in validation.

## 🏗️ Architecture

### The MCP Pattern (5 Components)

```
┌──────────────────────────────────────────────────────────────┐
│                        USER QUERY                             │
│          "What is the current price of gold and silver?"     │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────────┐
         │    COMPONENT 1: PLANNER           │
         │  • Analyzes query                 │
         │  • Breaks into steps              │
         │  • Identifies dependencies        │
         └────────────┬──────────────────────┘
                      │
                      │ Step 1: Get gold price
                      │ Step 2: Get silver price
                      │
                      ▼
         ┌───────────────────────────────────┐
         │  COMPONENT 2: TOOL SELECTOR       │
         │  • Validates tool choices         │
         │  • Prepares tool inputs           │
         │  • Resolves dependencies          │
         └────────────┬──────────────────────┘
                      │
                      │ Step 1 → commodity_price
                      │ Step 2 → commodity_price
                      │
                      ▼
         ┌───────────────────────────────────┐
         │   COMPONENT 3: EXECUTOR           │
         │  • Runs commodity_price("gold")   │
         │  • Runs commodity_price("silver") │
         │  • Collects all results           │
         └────────────┬──────────────────────┘
                      │
                      │ Results: {1: $4940, 2: $86.57}
                      │
                      ▼
         ┌───────────────────────────────────┐
         │   COMPONENT 4: VALIDATOR (NEW!)   │
         │  • Cross-checks results           │
         │  • Validates reasonableness       │
         │  • Checks consistency             │
         │  • Assesses data quality          │
         │  • Confidence scoring (0-100)     │
         └────────────┬──────────────────────┘
                      │
                      │ Validation: 95% confidence
                      │ Warnings: Future timestamps detected
                      │ Recommendation: RETRY_WITH_CAUTION
                      │
                      ▼
         ┌───────────────────────────────────┐
         │   COMPONENT 5: SYNTHESIZER        │
         │  • Combines results               │
         │  • Generates natural response     │
         │  • Formats for user               │
         └────────────┬──────────────────────┘
                      │
                      ▼
         ┌───────────────────────────────────┐
         │         FINAL RESPONSE             │
         │  "The current price of gold is    │
         │   $4940.0 USD and silver is       │
         │   $86.57 USD."                    │
         └───────────────────────────────────┘
```

## 📁 File Structure

```
backend/
├── app/
│   ├── api/
│   │   └── mcp.py                    # API endpoints for MCP agents
│   └── services/
│       ├── mcp_style_agent.py        # 🆕 MCP Style Agent (5-component)
│       ├── mcp_agent.py              # Original MCP-enhanced Langchain agent
│       └── mcp_server.py             # MCP server with resources and tools
└── test_validator.py                  # 🆕 Validator component test script
```

## 🔧 Components Deep Dive

### Component 1: Planner

**Role:** Strategic planning and task decomposition

**Responsibilities:**
- Analyze user's natural language query
- Break down into sequential steps
- Identify which tools are needed
- Determine dependencies between steps
- Create a structured execution plan

**Input:** User query (string)

**Output:** List of `PlanStep` objects

**Example:**
```python
Query: "Calculate 100 + 50 and analyze the result"

Plan:
  Step 1: Calculate 100 + 50
    → Tool: CALCULATOR
    → Input: "100 + 50"
    → Dependencies: []
  
  Step 2: Analyze the calculation result
    → Tool: TEXT_ANALYZER
    → Input: "result from step 1"
    → Dependencies: [1]
```

**Key Code:**
```python
class Planner:
    def create_plan(self, query: str) -> List[PlanStep]:
        # Uses LLM to create structured plan
        # Returns list of steps with tools and dependencies
        pass
```

### Component 2: Tool Selector

**Role:** Tool management and validation

**Responsibilities:**
- Validate tool selections from Planner
- Select the actual tool function to execute
- Prepare tool inputs
- Resolve dependencies (replace "result from step 1" with actual data)

**Input:** PlanStep + previous results

**Output:** Callable tool function + prepared input

**Example:**
```python
Step: "Analyze result from step 1"
Previous Results: {1: {"result": 150}}

Tool Selector:
  → Selects: AgentTools.text_analyzer
  → Prepares input: "150" (replaces reference with actual value)
  → Returns: (text_analyzer_func, "150")
```

**Key Code:**
```python
class ToolSelector:
    def select_tool(self, step: PlanStep) -> Optional[callable]:
        return self.available_tools.get(step.required_tool)
    
    def validate_tool_input(self, step: PlanStep, previous_results) -> str:
        # Resolves dependencies and prepares input
        pass
```

### Component 3: Executor

**Role:** Execution engine

**Responsibilities:**
- Execute each step in sequence
- Check dependencies before execution
- Handle errors gracefully
- Collect results from each step
- Provide execution summary

**Input:** List of PlanSteps

**Output:** Dictionary mapping step numbers to ExecutionResults

**Example:**
```python
Execution:
  Step 1: Calculate 100 + 50
    → Tool: calculator("100 + 50")
    → Result: {"expression": "100 + 50", "result": 150, "success": True}
    ✅ Success
  
  Step 2: Analyze "150"
    → Tool: text_analyzer("150")
    → Result: {"word_count": 1, "char_count": 3, ...}
    ✅ Success

Summary: 2/2 steps successful
```

**Key Code:**
```python
class Executor:
    def execute_plan(self, plan: List[PlanStep]) -> Dict[int, ExecutionResult]:
        results = {}
        for step in plan:
            tool = self.tool_selector.select_tool(step)
            input = self.tool_selector.validate_tool_input(step, results)
            output = tool(input)
            results[step.step_number] = ExecutionResult(...)
        return results
```

### Component 4: Validator (NEW!)

**Role:** Quality assurance and cross-checking

**Responsibilities:**
- Validate execution results for accuracy
- Check for data quality issues
- Assess reasonableness of results
- Detect inconsistencies or contradictions
- Provide confidence scoring (0-100)
- Generate warnings and recommendations

**Input:** Original query + Plan + Execution results

**Output:** Validation report (dict) with:
- `valid`: Boolean (True/False)
- `confidence_score`: 0-100
- `warnings`: List of potential issues
- `errors`: List of critical problems
- `recommendation`: ACCEPT / REJECT / RETRY_WITH_CAUTION
- `reasoning`: Detailed explanation

**Example:**
```python
Input:
  Query: "What is the current price of gold and silver?"
  Results: {
    1: {"current_price": 4940.0, "timestamp": "2026-02-03", "change_percent": 6.18},
    2: {"current_price": 86.57, "timestamp": "2026-02-03", "change_percent": 12.42}
  }

Validator Output:
  {
    "valid": True,
    "confidence_score": 95,
    "warnings": [
      "Future timestamp detected (2026-02-03)",
      "Unusually high change percentages (6.18%, 12.42%)"
    ],
    "errors": [],
    "recommendation": "RETRY_WITH_CAUTION",
    "reasoning": "Prices are plausible but data quality concerns exist..."
  }
```

**Validation Criteria:**
1. **Reasonableness**: Are values in expected ranges?
2. **Consistency**: Do results contradict each other?
3. **Completeness**: Were all required data points obtained?
4. **Data Quality**: Timestamps correct? Units valid?
5. **Relevance**: Do results actually answer the query?

**Key Code:**
```python
class Validator:
    def validate_results(
        self,
        original_query: str,
        plan: List[PlanStep],
        results: Dict[int, ExecutionResult]
    ) -> Dict[str, Any]:
        # Use LLM to cross-check results
        validation_prompt = """
        You are a validator. Assess these results for:
        1. Reasonableness
        2. Consistency
        3. Completeness
        4. Data quality
        5. Relevance to query
        
        Return JSON: {
          "valid": bool,
          "confidence_score": 0-100,
          "warnings": [...],
          "errors": [...],
          "recommendation": "ACCEPT|REJECT|RETRY_WITH_CAUTION",
          "reasoning": "..."
        }
        """
        return self.llm.invoke(validation_prompt)
```

### Component 5: Synthesizer

**Role:** Response generation

**Responsibilities:**
- Take all execution results
- Combine into coherent response
- Generate natural language
- Format for user consumption
- Hide internal details

**Input:** Original query + Plan + Execution results

**Output:** Natural language response (string)

**Example:**
```python
Input:
  Query: "Calculate 100 + 50 and analyze the result"
  Results: {
    1: {"result": 150},
    2: {"word_count": 1, "char_count": 3}
  }

Synthesizer Output:
  "100 plus 50 equals 150. The result is a 3-digit number
   consisting of 1 word. It's a simple numeric value."
```

**Key Code:**
```python
class Synthesizer:
    def synthesize_response(
        self,
        original_query: str,
        plan: List[PlanStep],
        results: Dict[int, ExecutionResult]
    ) -> str:
        # Uses LLM to generate natural response from results
        pass
```

## 🛠️ Available Tools

### 1. Search Tool

**Purpose:** Find information (mocked for demonstration)

**Use Cases:**
- Research queries
- Finding facts
- Getting current information

**Example:**
```python
search("Python programming")
→ {
    "query": "Python programming",
    "results": [
        {"title": "Python Docs", "snippet": "Python is..."},
        {"title": "Python Tutorial", "snippet": "Learn Python..."}
    ],
    "total_results": 2
}
```

### 2. Calculator Tool

**Purpose:** Perform mathematical calculations

**Use Cases:**
- Arithmetic operations
- Computing values
- Mathematical analysis

**Example:**
```python
calculator("25 * 4 + 10")
→ {
    "expression": "25 * 4 + 10",
    "result": 110,
    "success": True
}
```

**Safety:** Uses safe evaluation with restricted operations

### 3. Text Analyzer Tool

**Purpose:** Analyze text statistics

**Metrics:**
- Word count
- Character count
- Sentence count
- Average word length
- Average sentence length
- Longest word
- Readability score

**Example:**
```python
text_analyzer("The quick brown fox jumps over the lazy dog")
→ {
    "word_count": 9,
    "unique_words": 9,
    "sentence_count": 1,
    "avg_word_length": 3.89,
    "longest_word": "quick",
    "readability": "simple"
}
```

## 🚀 Usage

### Basic Usage

```python
from app.services.mcp_style_agent import run_mcp_agent

# Simple calculation
response = run_mcp_agent("What is 45 * 67?")
print(response)
# Output: "45 multiplied by 67 equals 3015."

# Text analysis
response = run_mcp_agent("Analyze this text: 'Hello World'")
print(response)
# Output: "The text 'Hello World' contains 2 words..."

# Combined operations
response = run_mcp_agent(
    "Search for Python and count words in 'Python is great'"
)
print(response)
```

### Advanced Usage

```python
from app.services.mcp_style_agent import MCPStyleAgent

# Initialize agent
agent = MCPStyleAgent(gemini_api_key="your-api-key")

# Run query
response = agent.run("Calculate 100 + 250 and analyze the result")

# The agent automatically:
# 1. Plans the steps
# 2. Selects tools
# 3. Executes tools
# 4. Synthesizes response
```

### API Usage

```bash
# Query the agent via API
curl -X POST "http://localhost:8001/api/mcp/style-agent/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Calculate 25 * 4 and analyze the result"
  }'

# Get example queries
curl "http://localhost:8001/api/mcp/style-agent/examples" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get architecture info (no auth required)
curl "http://localhost:8001/api/mcp/style-agent/info"
```

## 📊 Example Queries by Category

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
"What is the readability of 'This is a simple test sentence'?"
```

### Search Operations
```
"Search for information about Python"
"Find details about LangChain"
"What is the current weather?"
```

### Combined Operations
```
"Calculate 25 * 4 and analyze the result as text"
"Search for Python and count the words in the results"
"Find information about LangChain and calculate the word count"
```

### Complex Multi-Step
```
"Search for Python, calculate 100 + 50, and analyze the text 'Machine Learning'"
"Calculate the sum of 25 and 75, then search for information about that number"
"Analyze 'Hello World' and calculate the word count times 10"
```

## 🔍 Observing the Reasoning Process

The agent logs its reasoning at each stage. Check your console/logs to see:

```
=========================================================================
🎬 STARTING MCP AGENT EXECUTION
=========================================================================

📥 USER QUERY: Calculate 25 * 4 and analyze the result

=========================================================================
🎯 PLANNER: Creating execution plan for query
=========================================================================

📋 PLAN CREATED (2 steps):
  Step 1: Calculate 25 * 4
    → Tool: calculator
    → Input: 25 * 4
  Step 2: Analyze the result
    → Tool: text_analyzer
    → Input: result from step 1 (depends on: [1])

=========================================================================
⚙️  EXECUTOR: Beginning plan execution
=========================================================================

🔄 Executing Step 1: Calculate 25 * 4
🧮 CALCULATOR TOOL: Evaluating '25 * 4'
   ✅ Step 1 completed successfully
   📊 Output: {'expression': '25 * 4', 'result': 100, 'success': True}

🔄 Executing Step 2: Analyze the result
📝 TEXT ANALYZER TOOL: Analyzing text (3 chars)
   ✅ Step 2 completed successfully
   📊 Output: {'word_count': 1, 'char_count': 3, ...}

=========================================================================
🎨 SYNTHESIZER: Creating final response
=========================================================================

   ✅ SYNTHESIS COMPLETE
   📝 Response length: 145 characters

=========================================================================
🎉 MCP AGENT EXECUTION COMPLETE
=========================================================================
```

## 🎓 Learning Points

### Why This Architecture?

1. **Modularity:** Each component can be tested, improved, or replaced independently
2. **Transparency:** Clear logging shows the agent's reasoning process
3. **Extensibility:** Easy to add new tools without changing core logic
4. **Maintainability:** Clean separation of concerns makes code easier to understand
5. **Debuggability:** Can inspect state at each stage

### Comparison with Simple Chains

**Simple Chain (Rigid):**
```
Input → LLM → Output
```
- Always the same path
- No tool usage
- Limited capabilities

**MCP Style Agent (Flexible):**
```
Input → Plan → Select Tools → Execute → Synthesize → Output
```
- Adapts to query
- Uses appropriate tools
- Multi-step reasoning

### Adding New Tools

To add a new tool:

1. **Create the tool function:**
```python
@staticmethod
def web_scraper(url: str) -> Dict[str, Any]:
    # Scrape webpage
    return {"url": url, "content": "..."}
```

2. **Add to ToolType enum:**
```python
class ToolType(Enum):
    WEB_SCRAPER = "web_scraper"
    # ... other tools
```

3. **Register in ToolSelector:**
```python
self.available_tools = {
    ToolType.WEB_SCRAPER: AgentTools.web_scraper,
    # ... other tools
}
```

4. **Done!** The Planner will automatically consider it for future queries.

## 🧪 Testing

### Unit Tests

Test each component independently:

```python
# Test Planner
def test_planner():
    planner = Planner(llm)
    plan = planner.create_plan("Calculate 2+2")
    assert len(plan) > 0
    assert plan[0].required_tool == ToolType.CALCULATOR

# Test Tool Selector
def test_tool_selector():
    selector = ToolSelector()
    step = PlanStep(1, "Calculate", ToolType.CALCULATOR, [], "2+2")
    tool = selector.select_tool(step)
    assert tool is not None

# Test Executor
def test_executor():
    # Create mock plan
    # Execute
    # Assert results
    pass

# Test Synthesizer
def test_synthesizer():
    # Create mock results
    # Synthesize
    # Assert response quality
    pass
```

### Integration Tests

Test the full pipeline:

```python
def test_full_pipeline():
    agent = MCPStyleAgent()
    response = agent.run("What is 2+2?")
    assert "4" in response.lower()
```

## 🔐 Security Considerations

1. **Calculator:** Uses safe evaluation, no arbitrary code execution
2. **Search:** Mocked by default, validate input if using real API
3. **Text Analyzer:** Only analyzes text, no execution
4. **API:** Protected by authentication (except info endpoint)

## 🚀 Production Considerations

### For Production Use:

1. **Replace Mock Search:** Integrate real search API (Google, Bing, Elasticsearch)
2. **Add Caching:** Cache common calculations and searches
3. **Rate Limiting:** Limit LLM calls to prevent abuse
4. **Error Recovery:** Add retry logic for failed tool executions
5. **Monitoring:** Track agent performance and success rates
6. **Tool Timeout:** Add timeouts for long-running tools
7. **Result Validation:** Validate tool outputs before synthesis

### Performance Optimization:

1. **Parallel Execution:** Execute independent steps in parallel
2. **Streaming:** Stream responses for better UX
3. **Tool Selection Cache:** Cache tool selection decisions
4. **Batch Processing:** Process multiple queries together

## 📚 References

- **LangChain Agents:** https://python.langchain.com/docs/modules/agents/
- **ReAct Pattern:** https://arxiv.org/abs/2210.03629
- **Model Context Protocol:** https://modelcontextprotocol.io/

## 🆚 Comparison: MCP Style Agent vs MCP Enhanced Agent

This project has TWO different MCP implementations:

### MCP Enhanced Agent (`mcp_agent.py`)
- **Purpose:** Integrates Model Context Protocol resources/tools with LangChain
- **Pattern:** Traditional LangChain agent with MCP capabilities
- **Tools:** MCP server resources (knowledge base, system status, user stats)
- **Use Case:** When you need MCP protocol integration

### MCP Style Agent (`mcp_style_agent.py`) 🆕
- **Purpose:** Demonstrates Planner-Selector-Executor-Synthesizer pattern
- **Pattern:** Custom modular architecture with 4 distinct components
- **Tools:** Standalone tools (search, calculator, text analyzer)
- **Use Case:** Learning agent architecture, custom tool integration

**Use MCP Enhanced Agent when:** You need protocol-compliant MCP integration  
**Use MCP Style Agent when:** You want custom, modular agent architecture

## 📝 Next Steps

1. **Extend Tools:** Add more tools (database queries, API calls, file operations)
2. **UI Integration:** Build frontend components to show reasoning steps
3. **Advanced Planning:** Implement parallel execution for independent steps
4. **Learning:** Add memory so agent learns from past interactions
5. **Multi-Agent:** Create multiple specialized agents that collaborate

## 🤝 Contributing

To improve the MCP Style Agent:

1. Add new tools to `AgentTools` class
2. Improve planning prompts for better step generation
3. Enhance error handling and recovery
4. Add more comprehensive logging
5. Create visualization of agent reasoning

## 📄 License

Part of the Tothu AI Chat Application project.

---

**Built with:** Python, LangChain, Google Gemini, FastAPI  
**Pattern:** Planner-Selector-Executor-Synthesizer (MCP Style)  
**Status:** ✅ Fully Functional
