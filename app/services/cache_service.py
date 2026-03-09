import json
import aioredis
from typing import Optional
from app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = None
        self.prefix = "link:"
    
    async def get_redis(self):
        if not self.redis:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis
    
    async def cache_link(self, link, ttl: int = 3600):
        redis = await self.get_redis()
        key = f"{self.prefix}{link.short_code}"
        
        data = {
            "short_code": link.short_code,
            "original_url": link.original_url,
            "expires_at": link.expires_at.isoformat() if link.expires_at else None,
            "is_active": link.is_active
        }
        
        await redis.setex(key, ttl, json.dumps(data))
    
    async def get_cached_link(self, short_code: str) -> Optional[dict]:
        redis = await self.get_redis()
        key = f"{self.prefix}{short_code}"
        
        data = await redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def invalidate_cache(self, short_code: str):
        redis = await self.get_redis()
        key = f"{self.prefix}{short_code}"
        await redis.delete(key)
    
    async def cache_popular_links(self, links: list, ttl: int = 300):
        redis = await self.get_redis()
        data = [
            {
                "short_code": link.short_code,
                "original_url": link.original_url,
                "clicks": link.clicks
            }
            for link in links
        ]
        await redis.setex("popular_links", ttl, json.dumps(data))
    
    async def get_popular_links(self) -> Optional[list]:
        redis = await self.get_redis()
        data = await redis.get("popular_links")
        if data:
            return json.loads(data)
        return None