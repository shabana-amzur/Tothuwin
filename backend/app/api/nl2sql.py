"""
NL2SQL API Endpoints
Handles natural language to SQL query conversion and execution
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.models.database import User
from app.utils.auth import get_current_active_user
from app.services.nl2sql_service import get_nl2sql_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/nl-to-sql", tags=["nl2sql"])


# Request/Response Models
class NL2SQLRequest(BaseModel):
    """Request model for NL to SQL conversion"""
    question: str = Field(..., description="Natural language question", min_length=1, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Show total sales by month"
            }
        }


class NL2SQLResponse(BaseModel):
    """Response model for NL to SQL conversion"""
    success: bool = Field(..., description="Whether the query was successful")
    question: str = Field(..., description="Original question")
    sql: Optional[str] = Field(None, description="Generated SQL query")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Query results")
    row_count: Optional[int] = Field(None, description="Number of rows returned")
    columns: Optional[List[str]] = Field(None, description="Column names")
    error: Optional[str] = Field(None, description="Error message if any")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "question": "Show total sales by month",
                "sql": "SELECT DATE_TRUNC('month', date) as month, SUM(amount) as total FROM sales GROUP BY month",
                "data": [
                    {"month": "2024-01-01", "total": 15000},
                    {"month": "2024-02-01", "total": 18000}
                ],
                "row_count": 2,
                "columns": ["month", "total"],
                "error": None
            }
        }


class SchemaResponse(BaseModel):
    """Response model for database schema"""
    schema_info: str = Field(..., description="Database schema information", alias="schema")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "schema": "Table: users\nColumns:\n  - id: INTEGER NOT NULL\n  - email: VARCHAR NOT NULL"
            }
        }


@router.post(
    "/",
    response_model=NL2SQLResponse,
    summary="Convert natural language to SQL and execute",
    description="Converts a natural language question to a SQL SELECT query and executes it against the database"
)
async def nl_to_sql(
    request: NL2SQLRequest,
    current_user: User = Depends(get_current_active_user)
) -> NL2SQLResponse:
    """
    Convert natural language question to SQL and execute it
    
    **Security Features:**
    - Only SELECT queries allowed
    - Automatic validation of generated SQL
    - No write operations permitted (INSERT, UPDATE, DELETE, etc.)
    
    **Example Questions:**
    - "Show total sales by month"
    - "List top 5 customers by revenue"
    - "How many users registered last week?"
    - "What is the average order value?"
    """
    try:
        logger.info(f"User {current_user.email} asked: {request.question}")
        
        # Get NL2SQL service
        nl2sql_service = get_nl2sql_service()
        
        # Process the query
        result = nl2sql_service.process_nl_query(request.question)
        
        # Log the result
        if result['success']:
            logger.info(f"Query successful: {result.get('row_count', 0)} rows returned")
        else:
            logger.warning(f"Query failed: {result.get('error', 'Unknown error')}")
        
        return NL2SQLResponse(**result)
    
    except Exception as e:
        logger.error(f"Error in NL2SQL endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process natural language query: {str(e)}"
        )


@router.post(
    "/generate",
    response_model=Dict[str, Any],
    summary="Generate SQL without executing",
    description="Converts a natural language question to SQL without executing the query"
)
async def generate_sql_only(
    request: NL2SQLRequest,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Generate SQL query from natural language without executing it
    
    Useful for:
    - Previewing the generated SQL
    - Validating query generation
    - Learning SQL from natural language
    """
    try:
        logger.info(f"User {current_user.email} requested SQL generation for: {request.question}")
        
        # Get NL2SQL service
        nl2sql_service = get_nl2sql_service()
        
        # Generate SQL only
        result = nl2sql_service.generate_sql(request.question)
        
        return result
    
    except Exception as e:
        logger.error(f"Error generating SQL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SQL: {str(e)}"
        )


@router.get(
    "/schema",
    response_model=SchemaResponse,
    summary="Get database schema",
    description="Returns the database schema information for reference"
)
async def get_schema(
    current_user: User = Depends(get_current_active_user)
) -> SchemaResponse:
    """
    Get database schema information
    
    Returns table names, columns, data types, and relationships.
    Useful for understanding what data is available for querying.
    """
    try:
        logger.info(f"User {current_user.email} requested database schema")
        
        # Get NL2SQL service
        nl2sql_service = get_nl2sql_service()
        
        # Get schema
        schema = nl2sql_service.get_database_schema()
        
        return SchemaResponse(schema_info=schema)
    
    except Exception as e:
        logger.error(f"Error getting schema: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get database schema: {str(e)}"
        )


@router.post(
    "/validate",
    response_model=Dict[str, Any],
    summary="Validate a SQL query",
    description="Validates if a SQL query is safe to execute"
)
async def validate_sql(
    sql: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Validate a SQL query for safety
    
    Checks:
    - Only SELECT queries allowed
    - No dangerous keywords (INSERT, UPDATE, DELETE, etc.)
    - No SQL injection patterns
    - No multiple statements
    """
    try:
        from app.services.sql_validator import SQLValidator
        
        validator = SQLValidator()
        is_safe, sanitized_sql, error = validator.validate_and_sanitize(sql)
        
        return {
            'is_safe': is_safe,
            'sanitized_sql': sanitized_sql if is_safe else None,
            'error': error if not is_safe else None
        }
    
    except Exception as e:
        logger.error(f"Error validating SQL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate SQL: {str(e)}"
        )
