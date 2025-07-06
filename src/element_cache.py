"""
Element selector cache for storing successful xpath/CSS selectors
"""
import json
import hashlib
from typing import Dict, Optional, Any
from pathlib import Path
from loguru import logger


class ElementCache:
    """Cache for storing successful element selectors"""
    
    def __init__(self, cache_file: str = "element_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.load_cache()
    
    def _generate_key(self, url: str, element_description: str) -> str:
        """Generate unique key for caching"""
        combined = f"{url}::{element_description.lower().strip()}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, url: str, element_description: str) -> Optional[Dict[str, Any]]:
        """Get cached selector for element"""
        key = self._generate_key(url, element_description)
        result = self.cache.get(key)
        
        if result:
            logger.info(f"Cache hit for: {element_description}")
            return result
        
        logger.info(f"Cache miss for: {element_description}")
        return None
    
    def set(self, url: str, element_description: str, selector: str, 
            selector_type: str = "xpath", metadata: Optional[Dict] = None) -> None:
        """Store successful selector in cache"""
        key = self._generate_key(url, element_description)
        
        entry = {
            "selector": selector,
            "selector_type": selector_type,
            "url": url,
            "element_description": element_description,
            "metadata": metadata or {}
        }
        
        self.cache[key] = entry
        self.save_cache()
        
        logger.info(f"Cached selector for: {element_description} -> {selector}")
    
    def load_cache(self) -> None:
        """Load cache from file"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded cache with {len(self.cache)} entries")
            else:
                self.cache = {}
                logger.info("No cache file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self.cache = {}
    
    def save_cache(self) -> None:
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
            logger.debug(f"Saved cache with {len(self.cache)} entries")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def clear_cache(self) -> None:
        """Clear all cached entries"""
        self.cache = {}
        self.save_cache()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "cache_file": str(self.cache_file),
            "cache_size_bytes": self.cache_file.stat().st_size if self.cache_file.exists() else 0
        }