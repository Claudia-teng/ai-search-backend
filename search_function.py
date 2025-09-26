
import os
from typing import Dict, Any
from serpapi import GoogleSearch
import logging

logger = logging.getLogger(__name__)

def perform_web_search(query: str, num_results: int = 4) -> str:
    """
    Perform actual web search using SerpAPI
    This function will be called by the search agent
    Returns a string formatted for AutoGen
    """
    try:
        serpapi_key = os.getenv("SERPAPI_KEY")
        if not serpapi_key:
            raise ValueError("SERPAPI_KEY environment variable is required")
        
        # Configure SerpAPI search
        search_params = {
            "q": query,
            "api_key": serpapi_key,
            "num": num_results,
            "gl": "us",  # Country
            "hl": "en",  # Language
        }
        
        # Perform search
        search = GoogleSearch(search_params)
        results = search.get_dict()
        
        # Extract and structure results
        organic_results = results.get("organic_results", [])
        
        if not organic_results:
            return f"No search results found for query: {query}"
        
        # Format results as a readable string
        response = f"Search results for '{query}':\n\n"
        
        for i, result in enumerate(organic_results[:4], 1):  
            title = result.get("title", "No title")
            link = result.get("link", "")
            snippet = result.get("snippet", "No description available")
            
            # Use the helper functions
            domain = _extract_domain(link)
            relevance = _calculate_relevance(query, result)
            
            response += f"{i}. {title}\n"
            response += f"   URL: {link}\n"
            response += f"   Domain: {domain}\n"
            response += f"   Relevance: {relevance:.2f}\n"
            response += f"   Description: {snippet}\n\n"
        
        logger.info(f"Search completed for query: {query}, found {len(organic_results)} results")
        return response
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return f"Search error: {str(e)}"

def _extract_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return "unknown"

def _calculate_relevance(query: str, result: Dict[str, Any]) -> float:
    """Calculate relevance score for search result"""
    try:
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        query_words = query.lower().split()
        
        score = 0.0
        for word in query_words:
            if word in title:
                score += 0.5
            if word in snippet:
                score += 0.3
        
        return min(score, 1.0)
    except:
        return 0.0 