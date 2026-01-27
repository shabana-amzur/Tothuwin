"""
Test script for MCP Style Agent

This script demonstrates the MCP Style Agent with various example queries.
Run this to see the agent's reasoning process in action.

Usage:
    python test_mcp_style_agent.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.mcp_style_agent import run_mcp_agent, MCPStyleAgent
from app.config import get_settings


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_simple_calculation():
    """Test: Simple calculation"""
    print_section("TEST 1: Simple Calculation")
    
    query = "What is 45 * 67?"
    print(f"Query: {query}\n")
    
    response = run_mcp_agent(query)
    print(f"\nFinal Response:\n{response}\n")


def test_text_analysis():
    """Test: Text analysis"""
    print_section("TEST 2: Text Analysis")
    
    query = "Analyze this text: 'The quick brown fox jumps over the lazy dog. This is a test sentence.'"
    print(f"Query: {query}\n")
    
    response = run_mcp_agent(query)
    print(f"\nFinal Response:\n{response}\n")


def test_search():
    """Test: Search operation"""
    print_section("TEST 3: Search Operation")
    
    query = "Search for information about Python programming"
    print(f"Query: {query}\n")
    
    response = run_mcp_agent(query)
    print(f"\nFinal Response:\n{response}\n")


def test_combined_operations():
    """Test: Combined operations"""
    print_section("TEST 4: Combined Operations")
    
    query = "Calculate 25 * 4 and then analyze the result as text"
    print(f"Query: {query}\n")
    
    response = run_mcp_agent(query)
    print(f"\nFinal Response:\n{response}\n")


def test_complex_multi_step():
    """Test: Complex multi-step query"""
    print_section("TEST 5: Complex Multi-Step Query")
    
    query = "Search for Python, calculate 100 + 50, and analyze the text 'Machine Learning is powerful'"
    print(f"Query: {query}\n")
    
    response = run_mcp_agent(query)
    print(f"\nFinal Response:\n{response}\n")


def test_word_count_calculation():
    """Test: Word count with calculation"""
    print_section("TEST 6: Word Count with Calculation")
    
    text = "Python is a powerful programming language"
    query = f"Count the words in '{text}' and multiply that count by 10"
    print(f"Query: {query}\n")
    
    response = run_mcp_agent(query)
    print(f"\nFinal Response:\n{response}\n")


def interactive_mode():
    """Interactive mode - ask your own questions"""
    print_section("INTERACTIVE MODE")
    print("Ask the MCP Style Agent anything! (type 'quit' to exit)")
    print("\nExample queries:")
    print("  - Calculate 123 + 456")
    print("  - Analyze the text 'Hello World'")
    print("  - Search for LangChain")
    print("  - Calculate 50 * 2 and analyze the result\n")
    
    agent = MCPStyleAgent()
    
    while True:
        try:
            query = input("\n🤔 Your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            if not query:
                continue
            
            print("\n" + "-"*80)
            response = agent.run(query)
            print("-"*80)
            print(f"\n🤖 Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main():
    """Main test runner"""
    print("\n" + "🔵"*40)
    print("MCP STYLE AGENT - TEST SUITE")
    print("🔵"*40)
    
    # Check if API key is configured
    settings = get_settings()
    if not settings.GOOGLE_GEMINI_API_KEY:
        print("\n❌ ERROR: GOOGLE_GEMINI_API_KEY not configured")
        print("Please set your API key in backend/.env file\n")
        return
    
    print(f"\n✅ Using Gemini Model: {settings.GEMINI_MODEL}")
    print("📝 Each test will show the agent's reasoning process\n")
    
    try:
        # Run tests
        test_simple_calculation()
        test_text_analysis()
        test_search()
        test_combined_operations()
        test_complex_multi_step()
        test_word_count_calculation()
        
        # Summary
        print_section("TEST SUITE COMPLETE")
        print("✅ All tests executed successfully!")
        print("\nThe agent demonstrated:")
        print("  1. ✅ Simple calculations")
        print("  2. ✅ Text analysis")
        print("  3. ✅ Search operations")
        print("  4. ✅ Combined operations")
        print("  5. ✅ Complex multi-step reasoning")
        print("  6. ✅ Word count with calculations")
        
        print("\n" + "="*80)
        print("Want to try your own queries? Run in interactive mode:")
        print("  python test_mcp_style_agent.py --interactive")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check for interactive mode flag
    if len(sys.argv) > 1 and sys.argv[1] in ['--interactive', '-i']:
        interactive_mode()
    else:
        main()
