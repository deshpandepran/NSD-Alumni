import os
import json
import time
import logging
import hashlib
from typing import Optional, Dict, Any

# Ensure project directories exist
for folder in ['input', 'output', 'cache', 'logs', 'models']:
    os.makedirs(folder, exist_ok=True)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "pipeline.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("NSDPipeline")

class CacheManager:
    """Manages disk-based caching for search queries and scraped web content."""
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir

    def _get_hash(self, key: str) -> str:
        return hashlib.md5(key.encode('utf-8')).hexdigest()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        file_path = os.path.join(self.cache_dir, f"{self._get_hash(key)}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read cache file {file_path}: {e}")
        return None

    def set(self, key: str, value: Any) -> None:
        file_path = os.path.join(self.cache_dir, f"{self._get_hash(key)}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(value, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to write cache file {file_path}: {e}")

class RateLimiter:
    """Enforces delays between consecutive external requests to prevent IP blocks."""
    def __init__(self, delay_seconds: float = 2.0):
        self.delay_seconds = delay_seconds
        self.last_request_time = 0.0

    def wait(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            sleep_time = self.delay_seconds - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()

rate_limiter = RateLimiter(delay_seconds=2.5)
cache_manager = CacheManager()