import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

pytestmark = pytest.mark.functional

class TestLinks:
    
    async def test_create_link_unauthorized(self, client: AsyncClient, mock_db_session):
        """Тест создания ссылки без авторизации"""
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        response = await client.post("/api/links/shorten", json={
            "original_url": "https://example.com"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "short_code" in data
        assert data["is_custom"] == False
    
    async def test_create_link_authorized(self, client: AsyncClient, mock_db_session, auth_headers):
        """Тест создания ссылки с авторизацией"""
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        response = await client.post(
            "/api/links/shorten",
            json={"original_url": "https://example.com"},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "short_code" in data
        assert data["is_custom"] == False
    
    async def test_create_custom_link(self, client: AsyncClient, mock_db_session, auth_headers):
        """Тест создания кастомной ссылки"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        custom_alias = f"test{uuid4().hex[:6]}"
        response = await client.post(
            "/api/links/shorten",
            json={
                "original_url": "https://example.com",
                "custom_alias": custom_alias
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["short_code"] == custom_alias
        assert data["is_custom"] == True
    
    async def test_create_duplicate_custom_link(self, client: AsyncClient, mock_db_session, auth_headers):
        """Тест создания дублирующейся кастомной ссылки"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value={"short_code": "existing"})
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        response = await client.post(
            "/api/links/shorten",
            json={
                "original_url": "https://example.com",
                "custom_alias": "existing"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 409
        assert "already exists" in response.text
    
    async def test_create_link_with_expiration(self, client: AsyncClient, mock_db_session, auth_headers):
        """Тест создания ссылки с истекающим сроком"""
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        expires_at = "2025-12-31T23:59:59"
        response = await client.post(
            "/api/links/shorten",
            json={
                "original_url": "https://example.com",
                "expires_at": expires_at
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["expires_at"] is not None
    
    async def test_get_link_stats(self, client: AsyncClient, mock_db_session, auth_headers, test_link_obj):
        """Тест получения статистики"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=test_link_obj)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        response = await client.get(
            f"/api/links/{test_link_obj.short_code}/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == test_link_obj.short_code
    
    async def test_get_stats_unauthorized(self, client: AsyncClient, mock_db_session, test_link_obj):
        """Тест получения статистики без авторизации"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=test_link_obj)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        response = await client.get(f"/api/links/{test_link_obj.short_code}/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == test_link_obj.short_code
    
    async def test_update_link(self, client: AsyncClient, mock_db_session, auth_headers, test_link_obj):
        """Тест обновления ссылки"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=test_link_obj)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        new_url = "https://newexample.com"
        response = await client.put(
            f"/api/links/{test_link_obj.short_code}",
            json={"original_url": new_url},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_url"].rstrip('/') == new_url.rstrip('/')
    
    async def test_update_nonexistent_link(self, client: AsyncClient, mock_db_session, auth_headers):
        """Тест обновления несуществующей ссылки"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        response = await client.put(
            "/api/links/nonexistent",
            json={"original_url": "https://example.com"},
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_delete_link(self, client: AsyncClient, mock_db_session, auth_headers, test_link_obj):
        """Тест удаления ссылки"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=test_link_obj)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock()
        
        response = await client.delete(
            f"/api/links/{test_link_obj.short_code}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    async def test_delete_nonexistent_link(self, client: AsyncClient, mock_db_session, auth_headers):
        """Тест удаления несуществующей ссылки"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        response = await client.delete(
            "/api/links/nonexistent",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_search_links(self, client: AsyncClient, mock_db_session, auth_headers, test_link_obj):
        """Тест поиска ссылок"""
        mock_execute = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[test_link_obj])
        mock_execute.scalars = MagicMock(return_value=mock_scalars)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        response = await client.get(
            "/api/links/search",
            params={"original_url": "example"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
    
    async def test_search_without_auth(self, client: AsyncClient, mock_db_session, test_link_obj):
        """Тест поиска без авторизации"""
        mock_execute = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[test_link_obj])
        mock_execute.scalars = MagicMock(return_value=mock_scalars)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        response = await client.get(
            "/api/links/search",
            params={"original_url": "example"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        
        assert data[0]["short_code"] == test_link_obj.short_code