import time
from typing import List, Dict, Any
from duckduckgo_search import DDGS
from utils import logger, cache_manager, rate_limiter

def generate_queries(name: str, year: Any) -> List[str]:
    """Generates a targeted array of search phrases to minimize name ambiguity."""
    clean_name = name.strip()
    year_str = str(year).strip()
    
    return [
        f'"{clean_name}" "NSD" "{year_str}"',
        f'"{clean_name}" National School of Drama',
        f'"{clean_name}" theatre actor',
        f'"{clean_name}" theatre director',
        f'"{clean_name}" play',
        f'"{clean_name}" acted',
        f'"{clean_name}" directed',
        f'"{clean_name}" repertory',
        f'"{clean_name}" interview',
        f'"{clean_name}" portfolio',
        f'"{clean_name}" IMDb',
        f'"{clean_name}" LinkedIn',
        f'"{clean_name}" Instagram',
        f'"{clean_name}" Facebook',
        f'"{clean_name}" YouTube',
        f'"{clean_name}" website'
    ]

def search_person(name: str, year: Any, max_results_per_query: int = 2) -> List[Dict[str, str]]:
    """
    Executes multiple context-driven searches for an individual.
    Aggregates distinct target URLs while avoiding redundant network hits via caching.
    """
    queries = generate_queries(name, year)
    aggregated_results = {}
    
    logger.info(f"Starting web search discovery for: {name} ({year})")
    
    with DDGS() as ddgs:
        for query in queries:
            cache_key = f"search_v1_{query}"
            cached_data = cache_manager.get(cache_key)
            
            if cached_data is not None:
                results = cached_data
            else:
                rate_limiter.wait()
                try:
                    logger.debug(f"Executing web query: {query}")
                    results = list(ddgs.text(query, max_results=max_results_per_query))
                    cache_manager.set(cache_key, results)
                except Exception as e:
                    logger.error(f"Search failed for query '{query}': {e}")
                    results = []
                    time.sleep(5)  # Backoff penalty on failure
            
            for item in results:
                url = item.get("href")
                if url and url not in aggregated_results:
                    aggregated_results[url] = {
                        "title": item.get("title", ""),
                        "url": url,
                        "snippet": item.get("body", "")
                    }
                    
    return list(aggregated_results.values())