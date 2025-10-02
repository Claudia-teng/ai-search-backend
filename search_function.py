import logging
import os
import json

from serpapi import GoogleSearch


logger = logging.getLogger(__name__)

def perform_web_search(query: str, num_results: int = 4) -> dict:
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
        
        # Format results
        response = []
        for _, result in enumerate(organic_results[:4], 1):
            link = result.get("link", "")
            response.append(link)
        
        logger.info(f"Search completed for query: {query}, found {len(organic_results)} results")
        return json.dumps({"urls": response})
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return f"Search error: {str(e)}"