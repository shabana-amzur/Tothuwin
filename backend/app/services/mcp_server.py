"""
MCP (Model Context Protocol) Server Implementation
Provides structured context and tools to AI agents
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json


class MCPResource:
    """Represents an MCP resource (data/context)"""
    
    def __init__(self, uri: str, name: str, description: str, mime_type: str = "text/plain"):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
        self.content: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type,
            "content": self.content
        }


class MCPTool:
    """Represents an MCP tool (executable function)"""
    
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.input_schema = input_schema
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


class MCPServer:
    """
    MCP Server that provides resources and tools to agents
    Following the Model Context Protocol specification
    """
    
    def __init__(self):
        self.resources: List[MCPResource] = []
        self.tools: List[MCPTool] = []
        self._initialize_resources()
        self._initialize_tools()
    
    def _initialize_resources(self):
        """Initialize available resources"""
        
        # Company knowledge base
        company_kb = MCPResource(
            uri="context://company/knowledge-base",
            name="Company Knowledge Base",
            description="Information about company policies, products, and services"
        )
        company_kb.content = """
        # Company Information
        
        ## Products:
        1. AI Chat Assistant - Powered by Google Gemini
        2. SQL Query Interface - Natural language to SQL conversion
        3. Excel Analysis - AI-powered data analysis
        4. Image Validation - Document verification system
        5. Tic-Tac-Toe Game - Langchain agent-based game
        
        ## Policies:
        - Authentication: JWT + Google OAuth
        - Data Security: All data encrypted at rest
        - Privacy: User data never shared with third parties
        
        ## Support Hours: 24/7 automated support
        """
        self.resources.append(company_kb)
        
        # User guidelines
        guidelines = MCPResource(
            uri="context://company/guidelines",
            name="Usage Guidelines",
            description="Best practices and usage guidelines"
        )
        guidelines.content = """
        # Usage Guidelines
        
        ## Chat Assistant:
        - Ask clear, specific questions
        - Use markdown formatting in queries
        - Upload documents for context-aware responses
        
        ## SQL Queries:
        - Describe what data you need in plain English
        - Review generated SQL before execution
        - Use write operations with caution
        
        ## Excel Analysis:
        - Supports XLSX, XLS, CSV formats
        - Maximum file size: 50MB
        - Can connect to Google Sheets (public links only)
        
        ## Image Validation:
        - Supports invoices, receipts, ID cards
        - Demo mode available for testing
        - Results include confidence scores
        """
        self.resources.append(guidelines)
        
        # System status
        status = MCPResource(
            uri="context://system/status",
            name="System Status",
            description="Current system status and health metrics"
        )
        status.content = json.dumps({
            "status": "operational",
            "uptime": "99.9%",
            "active_users": "real-time data not available",
            "last_updated": datetime.now().isoformat(),
            "services": {
                "backend": "running",
                "frontend": "running",
                "database": "healthy",
                "ai_models": "loaded"
            }
        }, indent=2)
        self.resources.append(status)
    
    def _initialize_tools(self):
        """Initialize available tools"""
        
        # Get user statistics tool
        user_stats_tool = MCPTool(
            name="get_user_statistics",
            description="Get statistics about user activity and engagement",
            input_schema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "User ID to get statistics for"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["day", "week", "month", "all"],
                        "description": "Time period for statistics"
                    }
                },
                "required": ["user_id"]
            }
        )
        self.tools.append(user_stats_tool)
        
        # Search knowledge base tool
        search_kb_tool = MCPTool(
            name="search_knowledge_base",
            description="Search company knowledge base for specific information",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["products", "policies", "support", "all"],
                        "description": "Category to search in"
                    }
                },
                "required": ["query"]
            }
        )
        self.tools.append(search_kb_tool)
        
        # Generate report tool
        report_tool = MCPTool(
            name="generate_report",
            description="Generate various types of reports",
            input_schema={
                "type": "object",
                "properties": {
                    "report_type": {
                        "type": "string",
                        "enum": ["usage", "performance", "errors", "summary"],
                        "description": "Type of report to generate"
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Start date for report (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date",
                        "description": "End date for report (YYYY-MM-DD)"
                    }
                },
                "required": ["report_type"]
            }
        )
        self.tools.append(report_tool)
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources"""
        return [r.to_dict() for r in self.resources]
    
    def get_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Get a specific resource by URI"""
        for resource in self.resources:
            if resource.uri == uri:
                return resource.to_dict()
        return None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [t.to_dict() for t in self.tools]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments"""
        
        if tool_name == "get_user_statistics":
            return self._get_user_statistics(
                arguments.get("user_id"),
                arguments.get("period", "all")
            )
        
        elif tool_name == "search_knowledge_base":
            return self._search_knowledge_base(
                arguments.get("query"),
                arguments.get("category", "all")
            )
        
        elif tool_name == "generate_report":
            return self._generate_report(
                arguments.get("report_type"),
                arguments.get("start_date"),
                arguments.get("end_date")
            )
        
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    def _get_user_statistics(self, user_id: int, period: str) -> Dict[str, Any]:
        """Simulated user statistics"""
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "period": period,
                "statistics": {
                    "total_messages": 150,
                    "sql_queries": 25,
                    "excel_analyses": 10,
                    "image_validations": 5,
                    "games_played": 8,
                    "documents_uploaded": 12,
                    "avg_response_time": "1.2s",
                    "satisfaction_score": 4.5
                }
            }
        }
    
    def _search_knowledge_base(self, query: str, category: str) -> Dict[str, Any]:
        """Search knowledge base"""
        results = []
        
        for resource in self.resources:
            if resource.content and query.lower() in resource.content.lower():
                if category == "all" or category.lower() in resource.name.lower():
                    results.append({
                        "resource": resource.name,
                        "uri": resource.uri,
                        "description": resource.description,
                        "relevance": "high"
                    })
        
        return {
            "success": True,
            "query": query,
            "category": category,
            "results": results,
            "count": len(results)
        }
    
    def _generate_report(self, report_type: str, start_date: Optional[str], 
                        end_date: Optional[str]) -> Dict[str, Any]:
        """Generate a report"""
        return {
            "success": True,
            "report": {
                "type": report_type,
                "period": {
                    "start": start_date or "2026-01-01",
                    "end": end_date or datetime.now().strftime("%Y-%m-%d")
                },
                "summary": {
                    "total_requests": 1523,
                    "successful_requests": 1498,
                    "failed_requests": 25,
                    "avg_response_time": "1.3s",
                    "peak_usage_time": "14:00-16:00 UTC"
                },
                "generated_at": datetime.now().isoformat()
            }
        }
    
    def get_context_for_agent(self) -> str:
        """Get formatted context for AI agent"""
        context = "# Available MCP Resources\n\n"
        
        for resource in self.resources:
            context += f"## {resource.name}\n"
            context += f"**URI**: {resource.uri}\n"
            context += f"**Description**: {resource.description}\n"
            if resource.content:
                context += f"\n{resource.content}\n"
            context += "\n---\n\n"
        
        context += "# Available MCP Tools\n\n"
        for tool in self.tools:
            context += f"## {tool.name}\n"
            context += f"{tool.description}\n\n"
        
        return context


# Global MCP server instance
mcp_server = MCPServer()
