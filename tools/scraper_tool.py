from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup

@tool
def scrape_website(url: str):
    """
    Scrapes the content of a website.
    Args:
        url: The URL to scrape.
    Returns:
        The text content of the website.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Kill all script and style elements
            for script in soup(["script", "style"]):
                script.extract()    # rip it out
            
            text = soup.get_text()
            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text[:10000] # Return first 10k chars to avoid blowing up context
        else:
            return f"Error: Status code {response.status_code}"
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"
