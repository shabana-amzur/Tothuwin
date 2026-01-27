"""
Simple Demo of MCP Style Agent - WITHOUT LLM dependency

This demo shows the MCP pattern with hardcoded plans to demonstrate
the architecture without API key issues.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.mcp_style_agent import (
    AgentTools,
    PlanStep,
    ToolType,
    ToolSelector,
    Executor,
    ExecutionResult
)


def demo_calculator():
    """Demo: Simple calculator tool"""
    print("\n" + "="*70)
    print("DEMO 1: Calculator Tool")
    print("="*70)
    
    result = AgentTools.calculator("25 * 4")
    print(f"\nInput: '25 * 4'")
    print(f"Output: {result}")
    print(f"✅ Result: {result['result']}")


def demo_text_analyzer():
    """Demo: Text analyzer tool"""
    print("\n" + "="*70)
    print("DEMO 2: Text Analyzer Tool")
    print("="*70)
    
    text = "The quick brown fox jumps over the lazy dog"
    result = AgentTools.text_analyzer(text)
    print(f"\nInput: '{text}'")
    print(f"\nOutput:")
    print(f"  Word count: {result['word_count']}")
    print(f"  Unique words: {result['unique_words']}")
    print(f"  Character count: {result['text_length']}")
    print(f"  Average word length: {result['avg_word_length']}")
    print(f"  Longest word: {result['longest_word']}")
    print(f"  Readability: {result['readability']}")


def demo_search():
    """Demo: Search tool"""
    print("\n" + "="*70)
    print("DEMO 3: Search Tool")
    print("="*70)
    
    result = AgentTools.search("Python programming")
    print(f"\nQuery: 'Python programming'")
    print(f"\nResults found: {result['total_results']}")
    for i, res in enumerate(result['results'], 1):
        print(f"\n  {i}. {res['title']}")
        print(f"     {res['snippet']}")


def demo_manual_plan_execution():
    """Demo: Execute a manual plan (no LLM needed)"""
    print("\n" + "="*70)
    print("DEMO 4: Manual Plan Execution")
    print("="*70)
    print("\nQuery: 'Calculate 100 + 50 and analyze the result'\n")
    
    # Create a manual plan
    plan = [
        PlanStep(
            step_number=1,
            description="Calculate 100 + 50",
            required_tool=ToolType.CALCULATOR,
            dependencies=[],
            tool_input="100 + 50"
        ),
        PlanStep(
            step_number=2,
            description="Analyze the result from step 1",
            required_tool=ToolType.TEXT_ANALYZER,
            dependencies=[1],
            tool_input="result from step 1"
        )
    ]
    
    print("📋 PLAN:")
    for step in plan:
        deps = f" (depends on: {step.dependencies})" if step.dependencies else ""
        print(f"  Step {step.step_number}: {step.description}")
        print(f"    → Tool: {step.required_tool.value}")
        print(f"    → Input: {step.tool_input}{deps}")
    
    # Execute the plan
    print("\n⚙️  EXECUTION:")
    tool_selector = ToolSelector()
    executor = Executor(tool_selector)
    
    results = executor.execute_plan(plan)
    
    # Display results
    print("\n📊 RESULTS:")
    for step_num, result in results.items():
        print(f"\n  Step {step_num}:")
        if result.success:
            print(f"    ✅ Success")
            if isinstance(result.output, dict):
                for key, value in result.output.items():
                    if key != 'success':
                        print(f"    {key}: {value}")
        else:
            print(f"    ❌ Failed: {result.error}")
    
    # Manual synthesis (without LLM)
    print("\n🎨 SYNTHESIZER OUTPUT:")
    calc_result = results[1].output
    analysis_result = results[2].output
    
    response = f"""
100 plus 50 equals {calc_result['result']}.

Text Analysis of the result:
- Word count: {analysis_result['word_count']}
- Character count: {analysis_result['text_length']}
- The result "{calc_result['result']}" is a simple numeric value.
"""
    print(response)


def demo_complex_plan():
    """Demo: More complex multi-step plan"""
    print("\n" + "="*70)
    print("DEMO 5: Complex Multi-Step Plan")
    print("="*70)
    print("\nQuery: 'Calculate 25 * 4, search for Python, analyze the calculation'\n")
    
    # Create complex plan
    plan = [
        PlanStep(
            step_number=1,
            description="Calculate 25 * 4",
            required_tool=ToolType.CALCULATOR,
            dependencies=[],
            tool_input="25 * 4"
        ),
        PlanStep(
            step_number=2,
            description="Search for Python",
            required_tool=ToolType.SEARCH,
            dependencies=[],
            tool_input="Python programming"
        ),
        PlanStep(
            step_number=3,
            description="Analyze the calculation result",
            required_tool=ToolType.TEXT_ANALYZER,
            dependencies=[1],
            tool_input="result from step 1"
        )
    ]
    
    print("📋 PLAN (3 steps, step 1 and 2 are independent, step 3 depends on 1):")
    for step in plan:
        deps = f" ← depends on step {step.dependencies}" if step.dependencies else " (independent)"
        print(f"  Step {step.step_number}: {step.description} {deps}")
    
    # Execute
    tool_selector = ToolSelector()
    executor = Executor(tool_selector)
    results = executor.execute_plan(plan)
    
    # Summary
    print("\n📊 EXECUTION SUMMARY:")
    print(f"  Step 1 (Calculate): {results[1].output['result']}")
    print(f"  Step 2 (Search): Found {results[2].output['total_results']} results")
    print(f"  Step 3 (Analyze): {results[3].output['word_count']} words")


def show_architecture():
    """Show the MCP architecture diagram"""
    print("\n" + "="*70)
    print("MCP STYLE AGENT ARCHITECTURE")
    print("="*70)
    
    print("""
┌──────────────────────────────────────────────────────────────┐
│                        USER QUERY                             │
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
                      ▼
         ┌───────────────────────────────────┐
         │  COMPONENT 2: TOOL SELECTOR       │
         │  • Validates tool choices         │
         │  • Prepares tool inputs           │
         │  • Resolves dependencies          │
         └────────────┬──────────────────────┘
                      │
                      ▼
         ┌───────────────────────────────────┐
         │   COMPONENT 3: EXECUTOR           │
         │  • Runs tools sequentially        │
         │  • Handles errors                 │
         │  • Collects results               │
         └────────────┬──────────────────────┘
                      │
                      ▼
         ┌───────────────────────────────────┐
         │  COMPONENT 4: SYNTHESIZER         │
         │  • Combines results               │
         │  • Generates response             │
         │  • Formats for user               │
         └────────────┬──────────────────────┘
                      │
                      ▼
         ┌───────────────────────────────────┐
         │         FINAL RESPONSE             │
         └───────────────────────────────────┘

Available Tools:
  🔍 SEARCH: Find information (mocked)
  🧮 CALCULATOR: Perform calculations
  📝 TEXT_ANALYZER: Analyze text statistics
""")


def main():
    """Run all demos"""
    print("\n" + "🔵"*35)
    print("MCP STYLE AGENT - SIMPLE DEMO")
    print("(No LLM/API required for basic functionality)")
    print("🔵"*35)
    
    show_architecture()
    
    # Demo individual tools
    demo_calculator()
    demo_text_analyzer()
    demo_search()
    
    # Demo plan execution
    demo_manual_plan_execution()
    demo_complex_plan()
    
    print("\n" + "="*70)
    print("✅ ALL DEMOS COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Each component (Planner, Selector, Executor, Synthesizer) is modular")
    print("  2. Tools can be tested independently")
    print("  3. Plans can be created manually or by LLM")
    print("  4. Executor handles dependencies automatically")
    print("  5. The pattern is extensible - easy to add new tools")
    
    print("\n📚 For full LLM-powered agent, see:")
    print("  - app/services/mcp_style_agent.py")
    print("  - MCP_STYLE_AGENT_GUIDE.md")
    print("  - API endpoint: POST /api/mcp/style-agent/query")
    print("")


if __name__ == "__main__":
    main()
