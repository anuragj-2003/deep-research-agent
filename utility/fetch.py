import httpx
import trafilatura
from typing import Optional
from state.state import Doc

def clean_text(txt: str, max_chars: int = 40_000) -> str:
    """
    Cleans up whitespace and truncates string.
    """
    import re
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt[:max_chars]

def web_fetch(url: str, timeout: float = 25.0) -> Optional[Doc]:
    """
    Fetches web content using httpx and trafilatura.
    Junior-level try-catch implementations for fail-safes.
    """
    if not url or not url.startswith(("http://", "https://")):
        return None
        
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout, headers={"User-Agent":"DeepResearchAgent/1.0"}) as client:
            response = client.get(url)
            response.raise_for_status()
            
            # Extract main text
            downloaded = trafilatura.extract(
                response.text, 
                include_comments=False, 
                include_images=False, 
                url=url
            )
            
            content = clean_text(downloaded if downloaded else response.text)
            
            # Basic regex to grab title
            import re
            title_match = re.search(r"<title>(.*?)</title>", response.text, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else url
            
            return {
                "url": url, 
                "title": title, 
                "summary": "", 
                "content": content
            }
            
    except httpx.RequestError as e:
        print(f"Request Error fetching URL '{url}': {e}")
        return None
    except Exception as e:
        print(f"General Error fetching URL '{url}': {e}")
        return None
