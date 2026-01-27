"""
MCP-Enhanced Langchain Agent
Integrates Model Context Protocol with Langchain for enhanced context awareness
"""

from typing import List, Optional, Any, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import StructuredTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from app.services.mcp_server import mcp_server
import json


class MCPEnhancedAgent:
    """
    Langchain agent enhanced with MCP (Model Context Protocol) capabilities
    """
    
    def __init__(self, gemini_api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=gemini_api_key,
            temperature=0.7
        )
        self.mcp_server = mcp_server
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[StructuredTool]:
        """Create Langchain tools from MCP tools and add standard tools"""
        
        tools = []
        
        # MCP Resource Access Tool
        tools.append(StructuredTool.from_function(
            name="mcp_get_resource",
            description="Get content from MCP resources. Available resources: company knowledge base, usage guidelines, system status",
            func=self._get_mcp_resource
        ))
        
        # MCP Tool Execution
        tools.append(StructuredTool.from_function(
            name="mcp_search_knowledge",
            description="Search the company knowledge base for information about products, policies, or support",
            func=lambda query: self._execute_mcp_tool("search_knowledge_base", {"query": query})
        ))
        
        tools.append(StructuredTool.from_function(
            name="mcp_get_user_stats",
            description="Get user statistics and activity information. Requires user_id as input.",
            func=lambda user_id: self._execute_mcp_tool("get_user_statistics", {"user_id": int(user_id)})
        ))
        
        tools.append(StructuredTool.from_function(
            name="mcp_generate_report",
            description="Generate reports (usage, performance, errors, summary). Input should be report type.",
            func=lambda report_type: self._execute_mcp_tool("generate_report", {"report_type": report_type})
        ))
        
        # Standard tools
        tools.append(StructuredTool.from_function(
            name="calculator",
            description="Perform mathematical calculations. Input should be a mathematical expression.",
            func=self._calculator
        ))
        
        tools.append(StructuredTool.from_function(
            name="current_datetime",
            description="Get current date and time",
            func=self._get_datetime
        ))
        
        return tools
    
    def _get_mcp_resource(self, uri: str) -> str:
        """Get MCP resource content"""
        resource = self.mcp_server.get_resource(uri)
        if resource:
            return json.dumps(resource, indent=2)
        
        # If no exact match, list available resources
        resources = self.mcp_server.list_resources()
        return f"Resource not found. Available resources:\n" + \
               "\n".join([f"- {r['uri']}: {r['name']}" for r in resources])
    
    def _execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute an MCP tool"""
        result = self.mcp_server.execute_tool(tool_name, arguments)
        return json.dumps(result, indent=2)
    
    def _calculator(self, expression: str) -> str:
        """Safe calculator"""
        try:
            # Remove any potentially dangerous characters
            safe_expr = expression.replace("^", "**")
            # Only allow basic math operations
            allowed_chars = "0123456789+-*/().** "
            if all(c in allowed_chars for c in safe_expr):
                result = eval(safe_expr)
                return f"{expression} = {result}"
            else:
                return "Invalid expression. Use only numbers and basic operators (+, -, *, /, **)"
        except Exception as e:
            return f"Error calculating: {str(e)}"
    
    def _get_datetime(self, _: str = "") -> str:
        """Get current datetime"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _create_agent(self) -> AgentExecutor:
        """Create the Langchain agent with MCP context"""
        
        # Get MCP context
        mcp_context = self.mcp_server.get_context_for_agent()
        
        # Create prompt with MCP context
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an intelligent AI assistant with access to the Model Context Protocol (MCP) for enhanced context awareness.

{mcp_context}

You have access to the following capabilities:
1. Company knowledge base (products, policies, support)
2. Usage guidelines and best practices
3. System status and health information
4. User statistics and analytics
5. Report generation
6. Mathematical calculations
7. Current date/time

When users ask questions:
- First check if relevant MCP resources exist
- Use MCP tools to get accurate, up-to-date information
- Provide detailed, helpful responses
- Reference specific resources when applicable

Always be helpful, accurate, and professional."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        return agent_executor
    
    def invoke(self, question: str, chat_history: Optional[List] = None) -> str:
        """
        Invoke the MCP-enhanced agent
        
        Args:
            question: User's question
            chat_history: Optional chat history for context
            
        Returns:
            Agent's response
        """
        try:
            response = self.agent.invoke({
                "input": question,
                "chat_history": chat_history or []
            })
            return response["output"]
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get list of available MCP resources"""
        return self.mcp_server.list_resources()
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools"""
        return self.mcp_server.list_tools()
