from typing import Dict, Any
from state.state import ResearchState
from utility.search import web_search

def search_worker(arg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a specific search subquery and adds hits to the state.
    """
    subquery = arg.get("q", "")
    round_id = arg.get("round", 0)
    print(f"[searcher] Searching: {subquery}")
    
    results = []
    try:
        hits = web_search(subquery, k=5)
        seen = set()
        
        for h in hits:
            url = h.get("url")
            if url and url not in seen:
                results.append(h)
                seen.add(url)
    except Exception as e:
        print(f"Error in search_worker for {subquery}: {e}")
        
    # Mark completion by appending round id to reducer list
    return {"searches": results, "search_marks": [round_id]}

def search_join(state: ResearchState) -> Dict[str, Any]:
    """
    Joins all search results and deduplicates them.
    """
    print("[searcher] Joining search results...")
    
    dedup = []
    seen = set()
    try:
        for h in state.get("searches", []):
            u = h.get("url")
            if u and u not in seen:
                seen.add(u)
                dedup.append(h)
                
        # Top 10 results
        dedup = dedup[:10]
    except Exception as e:
        print(f"Error in search_join: {e}")
        
    return {"searches": dedup}

def can_advance_after_search(state: ResearchState) -> str:
    """
    Barrier condition: determines if we have received enough search marks.
    """
    try:
        expected = state.get("expected_search", 0)
        current_round = state.get("search_round", 0)
        marks = state.get("search_marks", [])
        
        # Count marks matching current round
        done = sum(1 for rid in marks if rid == current_round)
        
        print(f"[router] Search barrier: {done}/{expected} workers done.")
        
        if expected == 0 or done >= expected:
            return "go"
        else:
            return "wait"
    except Exception as e:
        print(f"Error in can_advance_after_search: {e}")
        return "go" # Fallback advance
