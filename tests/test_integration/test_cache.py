import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient

from app.services.cache_service import CacheService

pytestmark = pytest.mark.integration

class TestCacheIntegration:
    """Тесты интеграции с кэшем"""
    
    async def test_cache_fallback_on_redis_failure(self, client: AsyncClient, monkeypatch):
        """Тест fallback при отказе Redis"""
        async def failing_get_redis():
            raise Exception("Redis connection failed")
        
        monkeypatch.setattr(CacheService, 'get_redis', failing_get_redis)
        
        response = await client.post("/api/links/shorten", json={
            "original_url": "https://example.com"
        })
        
        assert response.status_code in [201, 401]