from langchain_core.tools import tool
from tavily import TavilyClient
import os

@tool
def tavily_search(query: str):
    """
    Searches the web for information using the Tavily API.
    Args:
        query: The search query.
    Returns:
        A list of search results.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not found in environment."
    
    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, search_depth="advanced")
        return response.get("results", [])
    except Exception as e:
        return f"Error executing search: {str(e)}"
