"""
Async cache implementation for FastAPI VannaSQL integration.
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AsyncCache(ABC):
    """
    Define the interface for an async cache that can be used to store data in a FastAPI app.
    """

    @abstractmethod
    async def generate_id(self, *args, **kwargs) -> str:
        """
        Generate a unique ID for the cache.
        """
        pass

    @abstractmethod
    async def get(self, id: str, field: str) -> Optional[Any]:
        """
        Get a value from the cache.
        """
        pass

    @abstractmethod
    async def get_all(self, field_list: List[str]) -> List[Dict[str, Any]]:
        """
        Get all values from the cache.
        """
        pass

    @abstractmethod
    async def set(self, id: str, field: str, value: Any) -> None:
        """
        Set a value in the cache.
        """
        pass

    @abstractmethod
    async def delete(self, id: str) -> None:
        """
        Delete a value from the cache.
        """
        pass


class AsyncMemoryCache(AsyncCache):
    """
    Async in-memory cache implementation.
    """
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def generate_id(self, *args, **kwargs) -> str:
        return str(uuid.uuid4())

    async def set(self, id: str, field: str, value: Any) -> None:
        async with self._lock:
            if id not in self.cache:
                self.cache[id] = {}
            self.cache[id][field] = value

    async def get(self, id: str, field: str) -> Optional[Any]:
        async with self._lock:
            if id not in self.cache:
                return None
            return self.cache[id].get(field)

    async def get_all(self, field_list: List[str]) -> List[Dict[str, Any]]:
        async with self._lock:
            result = []
            for cache_id in self.cache:
                item = {"id": cache_id}
                for field in field_list:
                    item[field] = self.cache[cache_id].get(field)
                result.append(item)
            return result

    async def delete(self, id: str) -> None:
        async with self._lock:
            if id in self.cache:
                del self.cache[id]
