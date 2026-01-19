"""
SQL Validator Service
Ensures only safe, read-only queries are executed
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Dangerous SQL keywords that indicate write operations
DANGEROUS_KEYWORDS = [
    'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 
    'TRUNCATE', 'REPLACE', 'MERGE', 'GRANT', 'REVOKE',
    'EXECUTE', 'EXEC', 'CALL', 'BEGIN', 'COMMIT', 'ROLLBACK'
]

# Additional dangerous patterns
DANGEROUS_PATTERNS = [
    r';\s*(?:INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE)',  # Multiple statements
    r'--',  # SQL comments (could hide malicious code)
    r'/\*',  # Block comments
    r'\bINTO\s+OUTFILE\b',  # File operations
    r'\bLOAD_FILE\b',  # File operations
    r'\bEXEC\(',  # Execute function calls
    r'\bSYS\.',  # System procedures
    r'\bxp_',  # Extended procedures (MSSQL)
]


class SQLValidator:
    """Validates SQL queries for safety and security"""
    
    @staticmethod
    def is_safe_query(sql: str) -> Tuple[bool, str]:
        """
        Validates if a SQL query is safe to execute
        
        Args:
            sql: The SQL query to validate
            
        Returns:
            Tuple of (is_safe: bool, error_message: str)
        """
        if not sql or not sql.strip():
            return False, "Empty query provided"
        
        # Normalize the query for checking
        sql_upper = sql.upper().strip()
        
        # Check if query starts with SELECT
        if not sql_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        # Check for dangerous keywords
        for keyword in DANGEROUS_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', sql_upper):
                logger.warning(f"Dangerous keyword detected: {keyword}")
                return False, f"Query contains forbidden keyword: {keyword}"
        
        # Check for dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False, "Query contains forbidden pattern or syntax"
        
        # Check for multiple statements (SQL injection prevention)
        # Allow semicolon only at the end
        semicolon_count = sql.count(';')
        if semicolon_count > 1:
            return False, "Multiple SQL statements are not allowed"
        
        if semicolon_count == 1 and not sql.strip().endswith(';'):
            return False, "Semicolon found in middle of query"
        
        logger.info(f"SQL query validated successfully: {sql[:100]}...")
        return True, ""
    
    @staticmethod
    def sanitize_query(sql: str) -> str:
        """
        Sanitizes a SQL query by removing trailing semicolons and extra whitespace
        
        Args:
            sql: The SQL query to sanitize
            
        Returns:
            Sanitized SQL query
        """
        # Remove trailing semicolon
        sql = sql.strip()
        if sql.endswith(';'):
            sql = sql[:-1].strip()
        
        # Remove extra whitespace
        sql = ' '.join(sql.split())
        
        return sql
    
    @staticmethod
    def validate_and_sanitize(sql: str) -> Tuple[bool, str, str]:
        """
        Validates and sanitizes a SQL query
        
        Args:
            sql: The SQL query to validate and sanitize
            
        Returns:
            Tuple of (is_safe: bool, sanitized_sql: str, error_message: str)
        """
        is_safe, error = SQLValidator.is_safe_query(sql)
        
        if not is_safe:
            return False, "", error
        
        sanitized = SQLValidator.sanitize_query(sql)
        return True, sanitized, ""
