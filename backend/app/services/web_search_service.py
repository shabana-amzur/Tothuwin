"""
Web Search Service - DuckDuckGo Integration
Provides internet search capabilities for real-time information
"""

from duckduckgo_search import DDGS
from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for performing web searches using DuckDuckGo"""
    
    def __init__(self):
        """Initialize the web search service"""
        self.ddgs = DDGS()
        self.last_request_time = 0
        self.min_delay = 2  # Minimum 2 seconds between requests
        logger.info("WebSearchService initialized with DuckDuckGo")
    
    def _apply_rate_limit(self):
        """Apply rate limiting to avoid DuckDuckGo rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search(self, query: str, max_results: int = 5, retries: int = 3) -> List[Dict[str, str]]:
        """
        Perform a web search and return results with retry logic
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            retries: Number of retry attempts
            
        Returns:
            List of search results with title, snippet, and link
        """
        for attempt in range(retries):
            try:
                self._apply_rate_limit()
                
                # Create a new instance for each search to avoid connection issues
                ddgs = DDGS()
                results = []
                search_results = ddgs.text(query, max_results=max_results)
                
                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("body", ""),
                        "link": result.get("href", ""),
                    })
                
                logger.info(f"Found {len(results)} results for query: {query}")
                return results
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Web search attempt {attempt + 1}/{retries} failed: {error_msg}")
                
                if "ratelimit" in error_msg.lower() or "202" in error_msg:
                    # Rate limited - wait longer before retry
                    if attempt < retries - 1:
                        wait_time = (attempt + 1) * 5  # Progressive backoff: 5s, 10s, 15s
                        logger.info(f"Rate limited. Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    continue
                elif attempt < retries - 1:
                    # Other error - short wait before retry
                    time.sleep(2)
                    continue
                else:
                    # Final attempt failed
                    logger.error(f"Web search failed after {retries} attempts: {error_msg}")
                    return []
        
        return []
    
    def get_news(self, query: str, max_results: int = 5, retries: int = 3) -> List[Dict[str, str]]:
        """
        Search for news articles with retry logic
        
        Args:
            query: News search query
            max_results: Maximum number of results
            retries: Number of retry attempts
            
        Returns:
            List of news results
        """
        for attempt in range(retries):
            try:
                self._apply_rate_limit()
                
                # Create a new instance for each search
                ddgs = DDGS()
                results = []
                news_results = ddgs.news(query, max_results=max_results)
                
                for result in news_results:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("body", ""),
                        "link": result.get("url", ""),
                        "date": result.get("date", ""),
                        "source": result.get("source", ""),
                    })
                
                logger.info(f"Found {len(results)} news results for query: {query}")
                return results
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"News search attempt {attempt + 1}/{retries} failed: {error_msg}")
                
                if "ratelimit" in error_msg.lower() or "202" in error_msg:
                    if attempt < retries - 1:
                        wait_time = (attempt + 1) * 5
                        logger.info(f"Rate limited. Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    continue
                elif attempt < retries - 1:
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"News search failed after {retries} attempts: {error_msg}")
                    return []
        
        return []
    
    def format_search_results(self, results: List[Dict[str, str]]) -> str:
        """
        Format search results into a readable string
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Formatted string with search results
        """
        if not results:
            return "No search results found."
        
        formatted = "🔍 **Search Results:**\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"**{i}. {result['title']}**\n"
            formatted += f"{result['snippet']}\n"
            if result.get('date'):
                formatted += f"📅 {result['date']}"
                if result.get('source'):
                    formatted += f" | 📰 {result['source']}"
                formatted += "\n"
            formatted += f"🔗 {result['link']}\n\n"
        
        return formatted


# Singleton instance
_web_search_service = None

def get_web_search_service() -> WebSearchService:
    """Get or create the web search service singleton"""
    global _web_search_service
    if _web_search_service is None:
        _web_search_service = WebSearchService()
    return _web_search_service
