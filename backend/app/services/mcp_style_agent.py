"""
MCP-Style Agent Implementation
================================

This implements a Model-Controller-Processor style agent with 4 distinct components:

1. PLANNER: Breaks down user query into executable steps
2. TOOL SELECTOR: Determines which tools are needed for each step
3. EXECUTOR: Executes the selected tools and gathers results
4. SYNTHESIZER: Combines results into a coherent final response

MCP Pattern:
    User Query → Planner → Tool Selector → Executor → Synthesizer → Final Response

Each component is modular and can be tested/replaced independently.
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class ToolType(Enum):
    """Available tool types in our MCP agent"""
    SEARCH = "search"
    CALCULATOR = "calculator"
    TEXT_ANALYZER = "text_analyzer"
    NONE = "none"  # For steps that don't need tools


@dataclass
class PlanStep:
    """Represents a single step in the execution plan"""
    step_number: int
    description: str
    required_tool: ToolType
    dependencies: List[int]  # Which previous steps this depends on
    tool_input: str  # What to pass to the tool


@dataclass
class ExecutionResult:
    """Result from executing a single step"""
    step_number: int
    success: bool
    output: Any
    error: Optional[str] = None


# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

class AgentTools:
    """
    Collection of tools available to the MCP agent.
    Each tool has a simple, focused purpose.
    """
    
    @staticmethod
    def search(query: str) -> Dict[str, Any]:
        """
        Search tool - Mocked for demonstration
        In production, this would call a real search API (e.g., Google, Bing, internal KB)
        """
        logger.info(f"🔍 SEARCH TOOL: Searching for '{query}'")
        
        # Mock search results based on keywords
        mock_results = {
            "python": [
                {"title": "Python Official Docs", "snippet": "Python is a high-level programming language known for readability."},
                {"title": "Python Tutorial", "snippet": "Learn Python step by step with examples."}
            ],
            "langchain": [
                {"title": "LangChain Documentation", "snippet": "LangChain is a framework for developing LLM applications."},
                {"title": "LangChain Agents", "snippet": "Agents use LLMs to make decisions about which actions to take."}
            ],
            "weather": [
                {"title": "Weather Today", "snippet": "Current weather: Sunny, 72°F"}
            ],
            "default": [
                {"title": "Search Result 1", "snippet": f"Information about {query}"},
                {"title": "Search Result 2", "snippet": f"More details on {query}"}
            ]
        }
        
        # Find matching results
        results = mock_results.get("default")
        for keyword, data in mock_results.items():
            if keyword in query.lower():
                results = data
                break
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
    
    @staticmethod
    def calculator(expression: str) -> Dict[str, Any]:
        """
        Calculator tool - Evaluates mathematical expressions safely
        """
        logger.info(f"🧮 CALCULATOR TOOL: Evaluating '{expression}'")
        
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Remove any text, keep only numbers and operators
            cleaned_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            
            # Safe evaluation (only allow basic math operations)
            allowed_chars = set('0123456789+-*/(). ')
            if not all(c in allowed_chars for c in cleaned_expr):
                raise ValueError("Invalid characters in expression")
            
            result = eval(cleaned_expr, {"__builtins__": {}}, {})
            
            return {
                "expression": expression,
                "result": result,
                "success": True
            }
        
        except Exception as e:
            logger.error(f"Calculator error: {e}")
            return {
                "expression": expression,
                "result": None,
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def text_analyzer(text: str) -> Dict[str, Any]:
        """
        Text analysis tool - Analyzes text and provides statistics
        """
        logger.info(f"📝 TEXT ANALYZER TOOL: Analyzing text ({len(text)} chars)")
        
        try:
            # Basic text analysis
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # Character analysis
            char_count = len(text)
            char_count_no_spaces = len(text.replace(" ", ""))
            
            # Word analysis
            word_count = len(words)
            unique_words = len(set(word.lower() for word in words))
            avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
            
            # Sentence analysis
            sentence_count = len(sentences)
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Find longest word
            longest_word = max(words, key=len) if words else ""
            
            return {
                "text_length": char_count,
                "text_length_no_spaces": char_count_no_spaces,
                "word_count": word_count,
                "unique_words": unique_words,
                "sentence_count": sentence_count,
                "avg_word_length": round(avg_word_length, 2),
                "avg_sentence_length": round(avg_sentence_length, 2),
                "longest_word": longest_word,
                "longest_word_length": len(longest_word),
                "readability": "simple" if avg_word_length < 5 else "moderate" if avg_word_length < 7 else "complex"
            }
        
        except Exception as e:
            logger.error(f"Text analyzer error: {e}")
            return {
                "error": str(e),
                "success": False
            }


# ============================================================================
# COMPONENT 1: PLANNER
# ============================================================================

class Planner:
    """
    PLANNER Component: Breaks down user queries into executable steps.
    
    The Planner analyzes the user's request and creates a structured plan
    with sequential steps. Each step identifies:
    - What needs to be done
    - What tool is required
    - What input the tool needs
    - Dependencies on previous steps
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        logger.info("✅ Planner initialized")
    
    def create_plan(self, query: str) -> List[PlanStep]:
        """
        Creates a structured execution plan from a user query.
        
        Args:
            query: User's natural language query
            
        Returns:
            List of PlanStep objects representing the execution plan
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🎯 PLANNER: Creating execution plan for query: '{query}'")
        logger.info(f"{'='*70}")
        
        # Prompt for planning
        planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a strategic planner for an AI agent. Your job is to break down user queries into clear, executable steps.

Available tools:
1. SEARCH: Search for information (use for: research, finding facts, getting current info)
2. CALCULATOR: Perform mathematical calculations (use for: math operations, counting, computing)
3. TEXT_ANALYZER: Analyze text content (use for: word count, text stats, readability analysis)
4. NONE: No tool needed (use for: simple responses, greetings, clarifications)

For each step, provide:
- Step number
- Description of what to do
- Which tool to use (SEARCH, CALCULATOR, TEXT_ANALYZER, or NONE)
- What input to provide to the tool
- Dependencies (which previous steps must complete first)

Format your response as JSON array:
[
  {{
    "step": 1,
    "description": "Search for Python information",
    "tool": "SEARCH",
    "input": "Python programming language",
    "dependencies": []
  }},
  {{
    "step": 2,
    "description": "Analyze search results",
    "tool": "TEXT_ANALYZER",
    "input": "results from step 1",
    "dependencies": [1]
  }}
]

IMPORTANT: Return ONLY valid JSON, no other text."""),
            ("human", "{query}")
        ])
        
        try:
            # Get plan from LLM
            chain = planning_prompt | self.llm
            response = chain.invoke({"query": query})
            
            # Parse the response
            content = response.content.strip()
            
            # Extract JSON if wrapped in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            plan_data = json.loads(content)
            
            # Convert to PlanStep objects
            steps = []
            for step_data in plan_data:
                tool_name = step_data.get("tool", "NONE").upper()
                try:
                    tool_type = ToolType[tool_name]
                except KeyError:
                    logger.warning(f"Unknown tool '{tool_name}', using NONE")
                    tool_type = ToolType.NONE
                
                step = PlanStep(
                    step_number=step_data.get("step", len(steps) + 1),
                    description=step_data.get("description", ""),
                    required_tool=tool_type,
                    dependencies=step_data.get("dependencies", []),
                    tool_input=step_data.get("input", "")
                )
                steps.append(step)
            
            # Log the plan
            logger.info(f"\n📋 PLAN CREATED ({len(steps)} steps):")
            for step in steps:
                deps = f" (depends on: {step.dependencies})" if step.dependencies else ""
                logger.info(f"  Step {step.step_number}: {step.description}")
                logger.info(f"    → Tool: {step.required_tool.value}")
                logger.info(f"    → Input: {step.tool_input}{deps}")
            
            return steps
        
        except Exception as e:
            logger.error(f"❌ Planning error: {e}")
            logger.error(f"Response content: {content if 'content' in locals() else 'N/A'}")
            
            # Fallback: Create a simple single-step plan
            return [PlanStep(
                step_number=1,
                description="Process query directly",
                required_tool=ToolType.NONE,
                dependencies=[],
                tool_input=query
            )]


# ============================================================================
# COMPONENT 2: TOOL SELECTOR
# ============================================================================

class ToolSelector:
    """
    TOOL SELECTOR Component: Determines the appropriate tool for each step.
    
    The Tool Selector validates and potentially refines tool choices made by
    the Planner. It ensures tools are used appropriately and can suggest
    alternatives if needed.
    """
    
    def __init__(self):
        self.available_tools = {
            ToolType.SEARCH: AgentTools.search,
            ToolType.CALCULATOR: AgentTools.calculator,
            ToolType.TEXT_ANALYZER: AgentTools.text_analyzer,
        }
        logger.info("✅ Tool Selector initialized")
    
    def select_tool(self, step: PlanStep) -> Optional[callable]:
        """
        Selects and returns the appropriate tool function for a step.
        
        Args:
            step: The PlanStep to select a tool for
            
        Returns:
            The tool function to execute, or None if no tool needed
        """
        logger.info(f"\n🔧 TOOL SELECTOR: Selecting tool for step {step.step_number}")
        logger.info(f"   Requested tool: {step.required_tool.value}")
        
        if step.required_tool == ToolType.NONE:
            logger.info(f"   ✓ No tool required for this step")
            return None
        
        tool_func = self.available_tools.get(step.required_tool)
        
        if tool_func:
            logger.info(f"   ✓ Tool '{step.required_tool.value}' selected and ready")
        else:
            logger.warning(f"   ⚠️  Tool '{step.required_tool.value}' not available")
        
        return tool_func
    
    def validate_tool_input(self, step: PlanStep, previous_results: Dict[int, ExecutionResult]) -> str:
        """
        Validates and prepares the input for a tool, resolving dependencies.
        
        Args:
            step: The step to prepare input for
            previous_results: Results from previous steps
            
        Returns:
            The prepared input string for the tool
        """
        input_str = step.tool_input
        
        # Replace references to previous steps with actual results
        for dep_step in step.dependencies:
            if dep_step in previous_results:
                result = previous_results[dep_step]
                if result.success:
                    # Replace placeholders like "results from step 1" with actual data
                    placeholder = f"step {dep_step}"
                    if placeholder in input_str.lower():
                        input_str = str(result.output)
        
        logger.info(f"   📝 Prepared input: {input_str[:100]}...")
        return input_str


# ============================================================================
# COMPONENT 3: EXECUTOR
# ============================================================================

class Executor:
    """
    EXECUTOR Component: Executes tools and gathers results.
    
    The Executor runs the selected tools with the prepared inputs,
    handles errors gracefully, and collects results for the Synthesizer.
    """
    
    def __init__(self, tool_selector: ToolSelector):
        self.tool_selector = tool_selector
        logger.info("✅ Executor initialized")
    
    def execute_plan(self, plan: List[PlanStep]) -> Dict[int, ExecutionResult]:
        """
        Executes all steps in the plan sequentially.
        
        Args:
            plan: List of PlanSteps to execute
            
        Returns:
            Dictionary mapping step numbers to ExecutionResults
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"⚙️  EXECUTOR: Beginning plan execution")
        logger.info(f"{'='*70}")
        
        results: Dict[int, ExecutionResult] = {}
        
        for step in plan:
            logger.info(f"\n🔄 Executing Step {step.step_number}: {step.description}")
            
            try:
                # Check dependencies
                for dep in step.dependencies:
                    if dep not in results or not results[dep].success:
                        raise ValueError(f"Dependency step {dep} failed or not completed")
                
                # Select tool
                tool_func = self.tool_selector.select_tool(step)
                
                # Prepare input
                tool_input = self.tool_selector.validate_tool_input(step, results)
                
                # Execute
                if tool_func is None:
                    # No tool needed, just pass through
                    output = {"message": "No tool execution needed", "input": tool_input}
                    success = True
                else:
                    output = tool_func(tool_input)
                    success = True
                
                # Store result
                result = ExecutionResult(
                    step_number=step.step_number,
                    success=success,
                    output=output
                )
                results[step.step_number] = result
                
                logger.info(f"   ✅ Step {step.step_number} completed successfully")
                logger.info(f"   📊 Output: {str(output)[:200]}...")
            
            except Exception as e:
                logger.error(f"   ❌ Step {step.step_number} failed: {e}")
                result = ExecutionResult(
                    step_number=step.step_number,
                    success=False,
                    output=None,
                    error=str(e)
                )
                results[step.step_number] = result
        
        # Summary
        successful = sum(1 for r in results.values() if r.success)
        logger.info(f"\n{'='*70}")
        logger.info(f"📊 EXECUTION COMPLETE: {successful}/{len(results)} steps successful")
        logger.info(f"{'='*70}")
        
        return results


# ============================================================================
# COMPONENT 4: SYNTHESIZER
# ============================================================================

class Synthesizer:
    """
    SYNTHESIZER Component: Combines results into a coherent final response.
    
    The Synthesizer takes all execution results and creates a natural,
    user-friendly response that answers the original query.
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        logger.info("✅ Synthesizer initialized")
    
    def synthesize_response(
        self,
        original_query: str,
        plan: List[PlanStep],
        results: Dict[int, ExecutionResult]
    ) -> str:
        """
        Synthesizes a final response from execution results.
        
        Args:
            original_query: The user's original question
            plan: The execution plan that was followed
            results: The results from executing the plan
            
        Returns:
            A natural language response to the user
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🎨 SYNTHESIZER: Creating final response")
        logger.info(f"{'='*70}")
        
        # Prepare context for synthesis
        context_parts = []
        
        context_parts.append(f"Original Query: {original_query}\n")
        context_parts.append("Execution Results:\n")
        
        for step in plan:
            result = results.get(step.step_number)
            if result:
                context_parts.append(f"\nStep {step.step_number}: {step.description}")
                context_parts.append(f"Tool Used: {step.required_tool.value}")
                if result.success:
                    context_parts.append(f"Result: {json.dumps(result.output, indent=2)}")
                else:
                    context_parts.append(f"Error: {result.error}")
        
        context = "\n".join(context_parts)
        
        # Synthesis prompt
        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a response synthesizer. Your job is to take execution results from various tools and create a clear, helpful response for the user.

Guidelines:
1. Answer the user's original question directly
2. Use information from the execution results
3. Present data in a clear, organized way
4. If calculations were performed, show the results clearly
5. If searches were done, summarize key findings
6. If text was analyzed, present statistics in a readable format
7. Be concise but complete
8. Use a friendly, professional tone

Do not mention "steps", "tools", or internal processes. Just answer the question naturally."""),
            ("human", "{context}")
        ])
        
        try:
            # Generate response
            chain = synthesis_prompt | self.llm
            response = chain.invoke({"context": context})
            
            final_response = response.content.strip()
            
            logger.info(f"\n✅ SYNTHESIS COMPLETE")
            logger.info(f"📝 Response length: {len(final_response)} characters")
            
            return final_response
        
        except Exception as e:
            logger.error(f"❌ Synthesis error: {e}")
            
            # Fallback: Create a simple response from results
            fallback_parts = [f"Based on your query: {original_query}\n"]
            for step in plan:
                result = results.get(step.step_number)
                if result and result.success:
                    fallback_parts.append(f"- {step.description}: {result.output}")
            
            return "\n".join(fallback_parts)


# ============================================================================
# MAIN MCP AGENT CLASS
# ============================================================================

class MCPStyleAgent:
    """
    Main MCP-Style Agent that orchestrates all four components:
    Planner → Tool Selector → Executor → Synthesizer
    
    This agent provides a complete implementation of the MCP pattern
    with modular, testable components.
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the MCP Agent with all components.
        
        Args:
            gemini_api_key: Google Gemini API key (optional, will use settings if not provided)
        """
        settings = get_settings()
        api_key = gemini_api_key or settings.GOOGLE_GEMINI_API_KEY
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Initialize components
        self.planner = Planner(self.llm)
        self.tool_selector = ToolSelector()
        self.executor = Executor(self.tool_selector)
        self.synthesizer = Synthesizer(self.llm)
        
        logger.info("\n" + "="*70)
        logger.info("🚀 MCP-STYLE AGENT INITIALIZED")
        logger.info("="*70)
        logger.info("Components: ✅ Planner | ✅ Tool Selector | ✅ Executor | ✅ Synthesizer")
        logger.info("="*70 + "\n")
    
    def run(self, query: str) -> str:
        """
        Main entry point: Process a user query through the complete MCP pipeline.
        
        Args:
            query: User's natural language query
            
        Returns:
            Final synthesized response
            
        Example:
            >>> agent = MCPStyleAgent()
            >>> response = agent.run("Calculate 25 * 4 and analyze the text 'Hello World'")
            >>> print(response)
        """
        logger.info("\n" + "🔵"*35)
        logger.info("🎬 STARTING MCP AGENT EXECUTION")
        logger.info("🔵"*35 + "\n")
        logger.info(f"📥 USER QUERY: {query}\n")
        
        try:
            # Step 1: Planning
            plan = self.planner.create_plan(query)
            
            # Step 2 & 3: Tool Selection and Execution
            # (Tool selection happens inside executor)
            results = self.executor.execute_plan(plan)
            
            # Step 4: Synthesis
            final_response = self.synthesizer.synthesize_response(query, plan, results)
            
            logger.info("\n" + "🔵"*35)
            logger.info("🎉 MCP AGENT EXECUTION COMPLETE")
            logger.info("🔵"*35 + "\n")
            
            return final_response
        
        except Exception as e:
            logger.error(f"❌ Agent execution failed: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def run_mcp_agent(query: str, api_key: Optional[str] = None) -> str:
    """
    Convenience function to run the MCP agent with a single query.
    
    Args:
        query: User's question or request
        api_key: Optional Gemini API key
        
    Returns:
        Agent's response
        
    Example:
        >>> response = run_mcp_agent("What is 100 + 250?")
        >>> print(response)
        
        >>> response = run_mcp_agent("Analyze this text: 'The quick brown fox jumps over the lazy dog'")
        >>> print(response)
    """
    agent = MCPStyleAgent(gemini_api_key=api_key)
    return agent.run(query)


# ============================================================================
# EXAMPLE USAGE (for testing)
# ============================================================================

if __name__ == "__main__":
    # Example 1: Calculation
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Calculation")
    print("="*70)
    response = run_mcp_agent("What is 45 * 67?")
    print(f"\n📤 RESPONSE:\n{response}\n")
    
    # Example 2: Text Analysis
    print("\n" + "="*70)
    print("EXAMPLE 2: Text Analysis")
    print("="*70)
    text = "The quick brown fox jumps over the lazy dog. This is a test sentence."
    response = run_mcp_agent(f"Analyze this text and tell me the word count: {text}")
    print(f"\n📤 RESPONSE:\n{response}\n")
    
    # Example 3: Combined Query
    print("\n" + "="*70)
    print("EXAMPLE 3: Combined Operations")
    print("="*70)
    response = run_mcp_agent(
        "First search for information about Python, then calculate how many words are in 'Python is great'"
    )
    print(f"\n📤 RESPONSE:\n{response}\n")
