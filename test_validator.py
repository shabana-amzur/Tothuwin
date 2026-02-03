#!/usr/bin/env python3
"""
Test the MCP Style Agent with Validator component
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.mcp_style_agent import run_mcp_agent

def test_validator():
    """Test the validator with a real-time query"""
    print("\n" + "="*70)
    print("🧪 TESTING MCP STYLE AGENT WITH VALIDATOR")
    print("="*70 + "\n")
    
    # Test query that requires real-time data
    query = "What is the current price of gold and silver?"
    
    print(f"Query: {query}\n")
    print("Running agent with 5-component architecture:")
    print("  1. PLANNER - Create execution plan")
    print("  2. TOOL SELECTOR - Select appropriate tools")
    print("  3. EXECUTOR - Execute the plan")
    print("  4. VALIDATOR - Cross-check results")
    print("  5. SYNTHESIZER - Generate final response")
    print("\n" + "-"*70 + "\n")
    
    # Run the agent
    response = run_mcp_agent(query)
    
    print("\n" + "="*70)
    print("📊 FINAL RESPONSE:")
    print("="*70)
    print(response)
    print("="*70 + "\n")

if __name__ == "__main__":
    test_validator()
