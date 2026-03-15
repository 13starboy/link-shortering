import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock

pytestmark = pytest.mark.functional

class TestValidation:
    
    async def test_create_link_invalid_url(self, client: AsyncClient):
        """Тест создания ссылки с невалидным URL"""
        response = await client.post("/api/links/shorten", json={
            "original_url": "not-a-url"
        })
        
        assert response.status_code == 422
    
    async def test_create_link_missing_url(self, client: AsyncClient):
        """Тест создания ссылки без URL"""
        response = await client.post("/api/links/shorten", json={})
        
        assert response.status_code == 422
    
    async def test_custom_alias_too_short(self, client: AsyncClient, auth_headers):
        """Тест слишком короткого кастомного alias"""
        response = await client.post(
            "/api/links/shorten",
            json={
                "original_url": "https://example.com",
                "custom_alias": "ab"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    async def test_custom_alias_too_long(self, client: AsyncClient, auth_headers):
        """Тест слишком длинного кастомного alias"""
        response = await client.post(
            "/api/links/shorten",
            json={
                "original_url": "https://example.com",
                "custom_alias": "a" * 60
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    async def test_custom_alias_invalid_chars(self, client: AsyncClient, auth_headers):
        """Тест недопустимых символов в alias"""
        response = await client.post(
            "/api/links/shorten",
            json={
                "original_url": "https://example.com",
                "custom_alias": "test@#$"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    async def test_invalid_expires_at_format(self, client: AsyncClient, auth_headers):
        """Тест неверного формата даты истечения"""
        response = await client.post(
            "/api/links/shorten",
            json={
                "original_url": "https://example.com",
                "expires_at": "not-a-date"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422