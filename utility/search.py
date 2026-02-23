import os
from typing import List
from state.state import SearchHit

def web_search(query: str, k: int = 6) -> List[SearchHit]:
    """
    Performs a web search using Tavily API.
    Simple try-catch approach for junior-level readability.
    """
    hits: List[SearchHit] = []
    
    try:
        from tavily import TavilyClient
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return [{"query": query, "url": "", "title": "Missing TavilyKey", "snippet": "Tavily API key is missing."}]
        
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=k)
        
        # Safely extract results
        results = response.get("results", [])
        
        for item in results:
            url = item.get("url", "")
            title = item.get("title", url)
            snippet = item.get("content", item.get("snippet", ""))[:300]
            
            if url:
                hits.append({"query": query, "url": url, "title": title, "snippet": snippet})
                
        return hits[:k]
    
    except Exception as e:
        print(f"Error during web search for query '{query}': {e}")
        # Return empty list or fallback error snippet
        return [{"query": query, "url": "", "title": "Search Error", "snippet": f"An error occurred: {e}"}]
