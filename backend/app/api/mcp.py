"""
MCP (Model Context Protocol) API Endpoints
Demonstrates integration of MCP with Langchain agents
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.models.database import User
from app.utils.auth import get_current_active_user
from app.services.mcp_agent import MCPEnhancedAgent
from app.services.mcp_server import mcp_server
from app.services.mcp_style_agent import MCPStyleAgent, run_mcp_agent
import os

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

# Initialize MCP agents
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
mcp_agent = MCPEnhancedAgent(GOOGLE_GEMINI_API_KEY) if GOOGLE_GEMINI_API_KEY else None
mcp_style_agent = MCPStyleAgent(GOOGLE_GEMINI_API_KEY) if GOOGLE_GEMINI_API_KEY else None


class MCPQueryRequest(BaseModel):
    question: str
    use_mcp: bool = True


class MCPQueryResponse(BaseModel):
    answer: str
    resources_used: List[str]
    tools_used: List[str]


class MCPToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


@router.get("/resources")
async def list_mcp_resources(current_user: User = Depends(get_current_active_user)):
    """
    List all available MCP resources
    
    MCP resources provide structured context to AI agents including:
    - Company knowledge base
    - Usage guidelines
    - System status
    """
    try:
        resources = mcp_server.list_resources()
        return {
            "success": True,
            "count": len(resources),
            "resources": resources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/{uri:path}")
async def get_mcp_resource(
    uri: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific MCP resource by URI
    
    Example URIs:
    - context://company/knowledge-base
    - context://company/guidelines
    - context://system/status
    """
    try:
        resource = mcp_server.get_resource(uri)
        if resource:
            return {
                "success": True,
                "resource": resource
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Resource not found: {uri}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def list_mcp_tools(current_user: User = Depends(get_current_active_user)):
    """
    List all available MCP tools
    
    MCP tools are executable functions that agents can call:
    - get_user_statistics: Get user activity stats
    - search_knowledge_base: Search company KB
    - generate_report: Generate various reports
    """
    try:
        tools = mcp_server.list_tools()
        return {
            "success": True,
            "count": len(tools),
            "tools": tools
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/execute")
async def execute_mcp_tool(
    request: MCPToolRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute an MCP tool with given arguments
    
    Example request:
    {
        "tool_name": "search_knowledge_base",
        "arguments": {"query": "excel", "category": "products"}
    }
    """
    try:
        result = mcp_server.execute_tool(request.tool_name, request.arguments)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def mcp_chat(
    request: MCPQueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Chat with MCP-enhanced AI agent
    
    The agent has access to:
    - MCP resources (knowledge base, guidelines, system status)
    - MCP tools (search, statistics, reports)
    - Standard tools (calculator, datetime)
    
    Example questions:
    - "What products does the company offer?"
    - "Search for information about Excel analysis"
    - "Get user statistics for user ID 1"
    - "Generate a usage report"
    - "What is 25 * 42 + 100?"
    """
    if not mcp_agent:
        raise HTTPException(
            status_code=500,
            detail="MCP agent not initialized. Check GOOGLE_GEMINI_API_KEY in .env file."
        )
    
    try:
        # Invoke MCP agent
        answer = mcp_agent.invoke(request.question)
        
        return {
            "success": True,
            "question": request.question,
            "answer": answer,
            "mcp_enabled": request.use_mcp,
            "agent_type": "mcp_enhanced"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo")
async def mcp_demo(current_user: User = Depends(get_current_active_user)):
    """
    Get demo examples for MCP functionality
    """
    return {
        "title": "MCP (Model Context Protocol) Demo",
        "description": "Examples of how to use MCP-enhanced AI agent",
        "examples": [
            {
                "category": "Resource Access",
                "examples": [
                    {
                        "question": "What products does the company offer?",
                        "mcp_resource": "context://company/knowledge-base",
                        "expected": "Agent will access company knowledge base and list all products"
                    },
                    {
                        "question": "What are the usage guidelines for Excel analysis?",
                        "mcp_resource": "context://company/guidelines",
                        "expected": "Agent will retrieve Excel-specific guidelines"
                    },
                    {
                        "question": "What is the system status?",
                        "mcp_resource": "context://system/status",
                        "expected": "Agent will provide current system health information"
                    }
                ]
            },
            {
                "category": "Tool Execution",
                "examples": [
                    {
                        "question": "Search for information about SQL queries",
                        "mcp_tool": "search_knowledge_base",
                        "expected": "Agent will search KB and return relevant information"
                    },
                    {
                        "question": "Get statistics for user 1",
                        "mcp_tool": "get_user_statistics",
                        "expected": "Agent will retrieve user activity statistics"
                    },
                    {
                        "question": "Generate a usage report",
                        "mcp_tool": "generate_report",
                        "expected": "Agent will create a comprehensive usage report"
                    }
                ]
            },
            {
                "category": "Combined MCP + Tools",
                "examples": [
                    {
                        "question": "What products do we have and how many users are active?",
                        "uses": ["knowledge_base resource", "user_statistics tool"],
                        "expected": "Agent combines multiple MCP capabilities"
                    },
                    {
                        "question": "Calculate the total if 50 users used Excel and 30 used SQL",
                        "uses": ["calculator tool"],
                        "expected": "Agent uses calculator: 50 + 30 = 80"
                    }
                ]
            }
        ],
        "available_resources": mcp_server.list_resources(),
        "available_tools": mcp_server.list_tools()
    }


@router.get("/status")
async def mcp_status(current_user: User = Depends(get_current_active_user)):
    """Get MCP system status"""
    return {
        "mcp_server": "operational",
        "agent_initialized": mcp_agent is not None,
        "mcp_style_agent_initialized": mcp_style_agent is not None,
        "resources_count": len(mcp_server.list_resources()),
        "tools_count": len(mcp_server.list_tools()),
        "protocol_version": "1.0",
        "features": [
            "Resource management",
            "Tool execution",
            "Agent integration",
            "Context enhancement",
            "MCP Style Agent (Planner-Selector-Executor-Synthesizer)"
        ]
    }


# ============================================================================
# MCP STYLE AGENT ENDPOINTS
# ============================================================================

class MCPStyleQueryRequest(BaseModel):
    """Request model for MCP Style Agent"""
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Calculate 25 * 4 and analyze the text 'Hello World'"
            }
        }


class MCPStyleQueryResponse(BaseModel):
    """Response model for MCP Style Agent"""
    success: bool
    query: str
    response: str
    error: Optional[str] = None


@router.post("/style-agent/query", response_model=MCPStyleQueryResponse)
async def mcp_style_agent_query(
    request: MCPStyleQueryRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute a query using the MCP Style Agent
    
    This endpoint demonstrates the MCP pattern with 4 components:
    1. PLANNER: Breaks query into steps
    2. TOOL SELECTOR: Chooses appropriate tools
    3. EXECUTOR: Runs tools and gathers results
    4. SYNTHESIZER: Creates final response
    
    Available tools:
    - Search: Find information (mocked)
    - Calculator: Perform calculations
    - Text Analyzer: Analyze text statistics
    
    Example queries:
    - "What is 100 + 250?"
    - "Analyze this text: 'The quick brown fox jumps over the lazy dog'"
    - "Calculate 45 * 67 and tell me if it's greater than 3000"
    - "Search for Python and count words in 'Python is awesome'"
    """
    try:
        if not mcp_style_agent:
            raise HTTPException(
                status_code=503,
                detail="MCP Style Agent not initialized. Check GOOGLE_GEMINI_API_KEY."
            )
        
        # Run the agent
        response = mcp_style_agent.run(request.query)
        
        return MCPStyleQueryResponse(
            success=True,
            query=request.query,
            response=response
        )
    
    except Exception as e:
        return MCPStyleQueryResponse(
            success=False,
            query=request.query,
            response="",
            error=str(e)
        )


@router.get("/style-agent/examples")
async def mcp_style_agent_examples(current_user: User = Depends(get_current_active_user)):
    """
    Get example queries for the MCP Style Agent
    
    Returns a collection of example queries organized by category
    to help users understand the agent's capabilities.
    """
    return {
        "description": "MCP Style Agent with Planner-Selector-Executor-Synthesizer pattern",
        "components": [
            {
                "name": "Planner",
                "description": "Breaks user query into executable steps"
            },
            {
                "name": "Tool Selector",
                "description": "Determines which tools are needed for each step"
            },
            {
                "name": "Executor",
                "description": "Executes tools and gathers results"
            },
            {
                "name": "Synthesizer",
                "description": "Combines results into coherent final response"
            }
        ],
        "available_tools": [
            {
                "name": "Search",
                "description": "Search for information (mocked)",
                "example": "Search for Python programming"
            },
            {
                "name": "Calculator",
                "description": "Perform mathematical calculations",
                "example": "Calculate 25 * 4"
            },
            {
                "name": "Text Analyzer",
                "description": "Analyze text statistics",
                "example": "Analyze the text 'Hello World'"
            }
        ],
        "example_queries": [
            {
                "category": "Simple Calculation",
                "queries": [
                    "What is 45 * 67?",
                    "Calculate 100 + 250",
                    "What's 1500 divided by 5?"
                ]
            },
            {
                "category": "Text Analysis",
                "queries": [
                    "Analyze this text: 'The quick brown fox jumps over the lazy dog'",
                    "Count words in 'Hello World from Python'",
                    "What is the readability of 'This is a simple test sentence'?"
                ]
            },
            {
                "category": "Search",
                "queries": [
                    "Search for information about Python",
                    "Find details about LangChain",
                    "What is the current weather?"
                ]
            },
            {
                "category": "Combined Operations",
                "queries": [
                    "Search for Python and count the words in the results",
                    "Calculate 25 * 4 and then analyze the result as text",
                    "Find information about LangChain and calculate the word count"
                ]
            },
            {
                "category": "Complex Multi-Step",
                "queries": [
                    "Search for Python, calculate 100 + 50, and analyze the text 'Machine Learning'",
                    "Calculate the sum of 25 and 75, then search for information about that number",
                    "Analyze 'Hello World' and calculate the word count times 10"
                ]
            }
        ],
        "usage_tips": [
            "Be specific in your queries for best results",
            "You can combine multiple operations in one query",
            "The agent will automatically plan and execute multi-step tasks",
            "Check logs to see the reasoning process (Planner → Selector → Executor → Synthesizer)"
        ]
    }


@router.get("/style-agent/info")
async def mcp_style_agent_info():
    """
    Get information about the MCP Style Agent architecture
    
    Public endpoint (no authentication required) that explains
    how the MCP Style Agent works.
    """
    return {
        "name": "MCP Style Agent",
        "pattern": "Model-Controller-Processor",
        "description": "A modular agent system with 4 distinct components working in sequence",
        "architecture": {
            "flow": "User Query → Planner → Tool Selector → Executor → Synthesizer → Final Response",
            "components": {
                "planner": {
                    "role": "Strategic planning",
                    "input": "User's natural language query",
                    "output": "Structured execution plan with steps",
                    "description": "Analyzes the query and breaks it into actionable steps, identifying which tools are needed"
                },
                "tool_selector": {
                    "role": "Tool management",
                    "input": "Plan steps from Planner",
                    "output": "Selected tool functions",
                    "description": "Validates tool choices and prepares tool inputs, resolving dependencies between steps"
                },
                "executor": {
                    "role": "Execution engine",
                    "input": "Plan + selected tools",
                    "output": "Execution results for each step",
                    "description": "Runs tools sequentially, handles errors, and collects results for synthesis"
                },
                "synthesizer": {
                    "role": "Response generation",
                    "input": "Original query + execution results",
                    "output": "Natural language response",
                    "description": "Combines all results into a coherent, user-friendly answer"
                }
            }
        },
        "benefits": [
            "Modular: Each component can be tested and improved independently",
            "Transparent: Reasoning steps are logged and visible",
            "Extensible: Easy to add new tools",
            "Robust: Error handling at each stage"
        ],
        "tools": [
            {
                "name": "Search",
                "type": "Information retrieval",
                "implementation": "Mocked (returns sample results)"
            },
            {
                "name": "Calculator",
                "type": "Mathematical computation",
                "implementation": "Safe eval with limited operators"
            },
            {
                "name": "Text Analyzer",
                "type": "Natural language processing",
                "implementation": "Statistical text analysis"
            }
        ],
        "example_flow": {
            "query": "Calculate 25 * 4 and analyze the result",
            "steps": [
                {
                    "stage": "Planner",
                    "action": "Creates 2-step plan: (1) Calculate, (2) Analyze"
                },
                {
                    "stage": "Tool Selector",
                    "action": "Selects Calculator for step 1, Text Analyzer for step 2"
                },
                {
                    "stage": "Executor",
                    "action": "Runs Calculator(25*4)→100, then Text Analyzer('100')→stats"
                },
                {
                    "stage": "Synthesizer",
                    "action": "Combines results: '25 * 4 = 100. The result has 3 characters...'"
                }
            ]
        }    }