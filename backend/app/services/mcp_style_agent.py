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
    FINANCIAL_DATA = "financial_data"
    COMMODITY_PRICE = "commodity_price"
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
        Search tool - Real-time web search using DuckDuckGo
        """
        logger.info(f"🔍 SEARCH TOOL: Searching for '{query}'")
        
        try:
            import requests
            from bs4 import BeautifulSoup
            import urllib.parse
            
            # Use DuckDuckGo HTML search
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return {
                    "query": query,
                    "results": [],
                    "total_results": 0,
                    "error": f"Search failed with status code: {response.status_code}"
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            search_results = soup.find_all('div', class_='result', limit=5)
            
            results = []
            for result in search_results:
                title_tag = result.find('a', class_='result__a')
                snippet_tag = result.find('a', class_='result__snippet')
                
                title = title_tag.text.strip() if title_tag else 'No title'
                snippet = snippet_tag.text.strip() if snippet_tag else 'No description'
                
                results.append({"title": title, "snippet": snippet})
            
            return {
                "query": query,
                "results": results,
                "total_results": len(results)
            }
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "error": str(e)
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


    @staticmethod
    def get_financial_data(symbol: str) -> Dict[str, Any]:
        """
        Get real-time stock, commodity, or cryptocurrency prices using Yahoo Finance
        """
        logger.info(f"💰 FINANCIAL DATA TOOL: Fetching data for '{symbol}'")
        
        try:
            import yfinance as yf
            from datetime import datetime
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            if not current_price:
                return {
                    "symbol": symbol,
                    "error": f"Could not fetch price for {symbol}",
                    "success": False
                }
            
            name = info.get('longName') or info.get('shortName') or symbol
            currency = info.get('currency', 'USD')
            
            # Calculate change percentage
            previous_close = info.get('previousClose', current_price)
            if previous_close and previous_close != 0:
                change_pct = ((current_price - previous_close) / previous_close) * 100
            else:
                change_pct = 0
            
            market_state = info.get('marketState', 'unknown')
            
            return {
                "symbol": symbol,
                "name": name,
                "current_price": current_price,
                "currency": currency,
                "change_percent": round(change_pct, 2),
                "market_state": market_state,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "success": True
            }
        except Exception as e:
            logger.error(f"Financial data error: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "success": False
            }
    
    @staticmethod
    def commodity_price(commodity: str) -> Dict[str, Any]:
        """
        Get current price for popular commodities (gold, silver, oil, etc.)
        """
        logger.info(f"💎 COMMODITY PRICE TOOL: Fetching price for '{commodity}'")
        
        # Map commodity names to Yahoo Finance symbols
        commodity_symbols = {
            'silver': 'SI=F',
            'gold': 'GC=F',
            'oil': 'CL=F',
            'crude oil': 'CL=F',
            'copper': 'HG=F',
            'platinum': 'PL=F',
            'palladium': 'PA=F',
            'natural gas': 'NG=F',
            'wheat': 'ZW=F',
            'corn': 'ZC=F',
            'soybeans': 'ZS=F'
        }
        
        commodity_lower = commodity.lower().strip()
        symbol = commodity_symbols.get(commodity_lower)
        
        if not symbol:
            available = ', '.join(commodity_symbols.keys())
            return {
                "commodity": commodity,
                "error": f"Unknown commodity. Available: {available}",
                "success": False
            }
        
        # Use get_financial_data to fetch the price
        result = AgentTools.get_financial_data(symbol)
        if result.get('success'):
            result['commodity'] = commodity
        return result


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
1. SEARCH: Search the web for real-time information (news, facts, current events)
2. CALCULATOR: Perform mathematical calculations (math operations, counting, computing)
3. TEXT_ANALYZER: Analyze text statistics (word count, readability, etc.)
4. FINANCIAL_DATA: Get stock/crypto prices (use ticker symbols like AAPL, BTC-USD, SI=F)
5. COMMODITY_PRICE: Get commodity prices (use names like silver, gold, oil, copper)
6. NONE: No tool needed (use for: simple responses, greetings, clarifications)

For each step, provide:
- Step number
- Description of what to do
- Which tool to use (SEARCH, CALCULATOR, TEXT_ANALYZER, FINANCIAL_DATA, COMMODITY_PRICE, or NONE)
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
            ToolType.FINANCIAL_DATA: AgentTools.get_financial_data,
            ToolType.COMMODITY_PRICE: AgentTools.commodity_price,
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
# COMPONENT 4: VALIDATOR
# ============================================================================

class Validator:
    """
    VALIDATOR Component: Cross-checks execution results for accuracy and consistency.
    
    The Validator ensures that tool outputs are reasonable, checks for contradictions,
    assigns confidence scores, and flags suspicious data before final synthesis.
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        logger.info("✅ Validator initialized")
    
    def validate_results(
        self,
        original_query: str,
        plan: List[PlanStep],
        results: Dict[int, ExecutionResult]
    ) -> Dict[str, Any]:
        """
        Validates execution results for accuracy and consistency.
        
        Args:
            original_query: The user's original question
            plan: The execution plan that was followed
            results: The results from executing the plan
            
        Returns:
            Validation report with confidence score and warnings
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"✓ VALIDATOR: Cross-checking results")
        logger.info(f"{'='*70}")
        
        # Prepare validation context
        context_parts = []
        context_parts.append(f"User Query: {original_query}\n")
        context_parts.append("Results to Validate:\n")
        
        for step in plan:
            result = results.get(step.step_number)
            if result:
                context_parts.append(f"\nStep {step.step_number}: {step.description}")
                context_parts.append(f"Tool: {step.required_tool.value}")
                if result.success:
                    context_parts.append(f"Output: {json.dumps(result.output, indent=2)}")
                else:
                    context_parts.append(f"Error: {result.error}")
        
        context = "\n".join(context_parts)
        
        # Validation prompt
        validation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a result validator. Analyze the execution results and check for:

1. **Reasonableness**: Do the results make sense? (e.g., is a silver price realistic?)
2. **Consistency**: Do multi-step results agree with each other?
3. **Completeness**: Did all required steps succeed?
4. **Data Quality**: Are there obvious errors or suspicious values?
5. **Relevance**: Do the results actually answer the user's question?

Provide your validation in JSON format:
{{
  "valid": true/false,
  "confidence_score": 0-100,
  "warnings": ["list of any concerns or issues"],
  "errors": ["list of critical problems if any"],
  "recommendation": "ACCEPT" or "REJECT" or "RETRY_WITH_CAUTION",
  "reasoning": "brief explanation of your assessment"
}}"""),
            ("human", "{context}")
        ])
        
        try:
            # Get validation assessment
            chain = validation_prompt | self.llm
            response = chain.invoke({"context": context})
            
            # Parse JSON response
            response_text = response.content.strip()
            
            # Extract JSON from markdown if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            validation_report = json.loads(response_text)
            
            # Log validation results
            logger.info(f"\n📋 VALIDATION REPORT:")
            logger.info(f"   Valid: {validation_report.get('valid', 'unknown')}")
            logger.info(f"   Confidence: {validation_report.get('confidence_score', 0)}%")
            logger.info(f"   Recommendation: {validation_report.get('recommendation', 'UNKNOWN')}")
            
            if validation_report.get('warnings'):
                logger.warning(f"   ⚠️  Warnings: {', '.join(validation_report['warnings'])}")
            
            if validation_report.get('errors'):
                logger.error(f"   ❌ Errors: {', '.join(validation_report['errors'])}")
            
            logger.info(f"   Reasoning: {validation_report.get('reasoning', 'N/A')}")
            
            return validation_report
        
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            
            # Fallback validation: Basic checks
            successful_steps = sum(1 for r in results.values() if r.success)
            total_steps = len(results)
            
            return {
                "valid": successful_steps == total_steps,
                "confidence_score": int((successful_steps / total_steps) * 100) if total_steps > 0 else 0,
                "warnings": [] if successful_steps == total_steps else ["Some steps failed"],
                "errors": [],
                "recommendation": "ACCEPT" if successful_steps == total_steps else "RETRY_WITH_CAUTION",
                "reasoning": f"Basic validation: {successful_steps}/{total_steps} steps succeeded"
            }


# ============================================================================
# COMPONENT 5: SYNTHESIZER
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
        self.validator = Validator(self.llm)
        self.synthesizer = Synthesizer(self.llm)
        
        logger.info("\n" + "="*70)
        logger.info("🚀 MCP-STYLE AGENT INITIALIZED")
        logger.info("="*70)
        logger.info("Components: ✅ Planner | ✅ Tool Selector | ✅ Executor | ✅ Validator | ✅ Synthesizer")
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
            
            # Step 4: Validation
            validation_report = self.validator.validate_results(query, plan, results)
            
            # Step 5: Synthesis (with validation context)
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
