import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
import time
import redis.asyncio as redis

from app.services.cache_service import CacheService

pytestmark = pytest.mark.unit

class TestCacheService:
    """Тесты для сервиса кэширования"""
    
    @pytest.fixture
    def cache_service(self):
        return CacheService()
    
    async def test_get_redis_success(self, cache_service):
            """Тест успешного подключения к Redis"""
            cache_service.redis = None
            cache_service.use_redis = True
            
            mock_redis_client = AsyncMock()
            mock_redis_client.ping = AsyncMock(return_value=True)
            mock_redis_client.get = AsyncMock(return_value=None)
            mock_redis_client.setex = AsyncMock()
            mock_redis_client.delete = AsyncMock()
            
            with patch('redis.asyncio.from_url') as mock_from_url:
                mock_from_url.return_value = mock_redis_client
                
                redis_client = await cache_service.get_redis()
                mock_from_url.assert_called_once()
    
    async def test_get_redis_failure_fallback(self, cache_service):
        with patch('redis.asyncio.from_url', side_effect=Exception("Connection failed")):
            redis = await cache_service.get_redis()
            
            assert redis is None
            assert cache_service.use_redis == False
    
    async def test_cache_link_with_redis(self, cache_service):
        """Тест кэширования ссылки с Redis"""
        mock_redis = AsyncMock()
        cache_service.redis = mock_redis
        cache_service.use_redis = True
        
        mock_link = MagicMock()
        mock_link.short_code = "test123"
        mock_link.original_url = "https://example.com"
        mock_link.expires_at = None
        mock_link.is_active = True
        
        await cache_service.cache_link(mock_link, ttl=60)
        
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == "link:test123"
        assert args[1] == 60
    
    async def test_cache_link_without_redis(self, cache_service):
        """Тест кэширования ссылки без Redis"""
        cache_service.redis = None
        cache_service.use_redis = False
        
        mock_link = MagicMock()
        mock_link.short_code = "test123"
        mock_link.original_url = "https://example.com"
        mock_link.expires_at = None
        mock_link.is_active = True
        
        await cache_service.cache_link(mock_link, ttl=60)
        
        assert "test123" in cache_service.local_cache
        assert cache_service.local_cache["test123"]["data"]["original_url"] == "https://example.com"
    
    async def test_get_cached_link_with_redis(self, cache_service):
        """Тест получения кэшированной ссылки из Redis"""
        mock_redis = AsyncMock()
        cached_data = json.dumps({
            "short_code": "test123",
            "original_url": "https://example.com",
            "expires_at": None,
            "is_active": True
        })
        mock_redis.get = AsyncMock(return_value=cached_data)
        cache_service.redis = mock_redis
        cache_service.use_redis = True
        
        result = await cache_service.get_cached_link("test123")
        
        assert result is not None
        assert result["short_code"] == "test123"
        mock_redis.get.assert_called_once_with("link:test123")
    
    async def test_get_cached_link_from_memory(self, cache_service):
        """Тест получения кэшированной ссылки из памяти"""
        cache_service.redis = None
        cache_service.use_redis = False
        cache_service.local_cache["test123"] = {
            "data": {
                "short_code": "test123",
                "original_url": "https://example.com"
            },
            "expires": time.time() + 60
        }
        
        result = await cache_service.get_cached_link("test123")
        
        assert result is not None
        assert result["short_code"] == "test123"
    
    async def test_get_cached_link_expired(self, cache_service):
        """Тест получения истекшей ссылки из памяти"""
        cache_service.redis = None
        cache_service.use_redis = False
        cache_service.local_cache["test123"] = {
            "data": {
                "short_code": "test123",
                "original_url": "https://example.com"
            },
            "expires": time.time() - 60
        }
        
        result = await cache_service.get_cached_link("test123")
        
        assert result is None
        assert "test123" not in cache_service.local_cache
    
    async def test_invalidate_cache_with_redis(self, cache_service):
        mock_redis = AsyncMock()
        cache_service.redis = mock_redis
        cache_service.use_redis = True
        
        await cache_service.invalidate_cache("test123")
        
        mock_redis.delete.assert_called_once_with("link:test123")
    
    async def test_invalidate_cache_without_redis(self, cache_service):
        cache_service.redis = None
        cache_service.use_redis = False
        cache_service.local_cache["test123"] = {"data": {}, "expires": time.time() + 60}
        
        await cache_service.invalidate_cache("test123")
        
        assert "test123" not in cache_service.local_cache
    
    async def test_cache_popular_links(self, cache_service):
        mock_redis = AsyncMock()
        cache_service.redis = mock_redis
        cache_service.use_redis = True
        
        mock_links = [
            MagicMock(short_code="test1", original_url="https://ex1.com", clicks=10),
            MagicMock(short_code="test2", original_url="https://ex2.com", clicks=5)
        ]
        
        await cache_service.cache_popular_links(mock_links, ttl=300)
        
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == "popular_links"
        assert args[1] == 300
    
    async def test_get_popular_links(self, cache_service):
        mock_redis = AsyncMock()
        cached_data = json.dumps([
            {"short_code": "test1", "original_url": "https://ex1.com", "clicks": 10}
        ])
        mock_redis.get = AsyncMock(return_value=cached_data)
        cache_service.redis = mock_redis
        cache_service.use_redis = True
        
        result = await cache_service.get_popular_links()
        
        assert result is not None
        assert len(result) == 1
        assert result[0]["short_code"] == "test1"