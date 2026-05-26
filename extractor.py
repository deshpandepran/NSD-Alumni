import requests
from bs4 import BeautifulSoup
from utils import logger, cache_manager, rate_limiter

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_url_content(url: str, timeout_seconds: int = 10) -> str:
    """
    Downloads text content from a given URL. 
    Maintains clean markdown/text output while stripping non-content structural HTML tags.
    """
    # Exclude social network deep links from direct scraping to avoid login blocks
    blacklist_domains = ["instagram.com", "linkedin.com", "facebook.com", "twitter.com", "x.com", "support.google.com", "microsoft.com", "learn.microsoft.com", "thewindowsclub.com"]
    if any(domain in url.lower() for domain in blacklist_domains):
        return ""

    cache_key = f"html_v1_{url}"
    cached_content = cache_manager.get(cache_key)
    if cached_content is not None:
        return cached_content.get("text", "")

    rate_limiter.wait()
    logger.info(f"Scraping content from URL: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout_seconds, allow_redirects=True)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch {url}. Status code: {response.status_code}")
            return ""
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove noisy structural/script components
        for element in soup(["script", "style", "nav", "header", "footer", "form"]):
            element.decompose()
            
        # Extract visible normalized text blocks
        text = soup.get_text(separator=" ")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)
        
        # Keep character limits reasonable for local LLM context ingestion
        truncated_text = clean_text[:6000]
        
        cache_manager.set(cache_key, {"text": truncated_text})
        return truncated_text

    except requests.RequestException as e:
        logger.error(f"Network error while requesting {url}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing text content for {url}: {e}")
        
    return ""