import json
import redis.asyncio as redis
from typing import Optional, Any
from app.config import get_settings

settings = get_settings()


class CacheService:
    def __init__(self):
        self.redis_url = settings.redis_url
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        if self._redis is None:
            self._redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            r = await self.connect()
            value = await r.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (seconds)"""
        try:
            r = await self.connect()
            await r.setex(key, ttl, json.dumps(value))
        except Exception as e:
            print(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete key from cache"""
        try:
            r = await self.connect()
            await r.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    async def get_audio_url(self, node_id: str, language: str, speaker: str) -> Optional[str]:
        """Get cached audio URL"""
        key = f"audio:{node_id}:{language}:{speaker}"
        return await self.get(key)
    
    async def set_audio_url(self, node_id: str, language: str, speaker: str, url: str, ttl: int = 86400 * 30):
        """Cache audio URL for 30 days"""
        key = f"audio:{node_id}:{language}:{speaker}"
        await self.set(key, url, ttl)
