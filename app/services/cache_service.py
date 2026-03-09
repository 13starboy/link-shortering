import json
import time
from typing import Optional
from redis import asyncio as aioredis
from app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis = None
        self.prefix = "link:"
        self.use_redis = True
        self.local_cache = {}

    async def get_redis(self):
        if not self.redis and self.use_redis:
            try:
                self.redis = await aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                await self.redis.ping()
            except Exception as e:
                print(f"⚠️ Redis not available, using in-memory cache: {e}")
                self.use_redis = False
                self.redis = None
        return self.redis if self.use_redis else None

    async def cache_link(self, link, ttl: int = 3600):
        redis = await self.get_redis()
        data = {
            "short_code": link.short_code,
            "original_url": link.original_url,
            "expires_at": link.expires_at.isoformat() if link.expires_at else None,
            "is_active": link.is_active
        }

        if redis:
            key = f"{self.prefix}{link.short_code}"
            await redis.setex(key, ttl, json.dumps(data))
        else:
            self.local_cache[link.short_code] = {
                "data": data,
                "expires": time.time() + ttl
            }

    async def get_cached_link(self, short_code: str) -> Optional[dict]:
        redis = await self.get_redis()

        if redis:
            key = f"{self.prefix}{short_code}"
            data = await redis.get(key)
            if data:
                return json.loads(data)
        else:
            cached = self.local_cache.get(short_code)
            if cached and cached["expires"] > time.time():
                return cached["data"]
            elif cached:
                del self.local_cache[short_code]

        return None

    async def invalidate_cache(self, short_code: str):
        redis = await self.get_redis()
        if redis:
            key = f"{self.prefix}{short_code}"
            await redis.delete(key)
        else:
            self.local_cache.pop(short_code, None)

    async def cache_popular_links(self, links: list, ttl: int = 300):
        redis = await self.get_redis()
        if not redis:
            return
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
        if not redis:
            return None
        data = await redis.get("popular_links")
        if data:
            return json.loads(data)
        return None