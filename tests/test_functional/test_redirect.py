import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

pytestmark = pytest.mark.functional

class TestRedirect:
    
    async def test_redirect_success(self, client: AsyncClient, mock_db_session, test_link_obj):
        """Тест успешного редиректа"""
        if not hasattr(test_link_obj, 'clicks'):
            test_link_obj.clicks = 0
        
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=test_link_obj)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        mock_db_session.commit = AsyncMock()
        
        response = await client.get(f"/api/{test_link_obj.short_code}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_url"] == test_link_obj.original_url
    
    async def test_redirect_nonexistent(self, client: AsyncClient, mock_db_session):
        """Тест редиректа по несуществующей ссылке"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        response = await client.get("/api/nonexistent")
        
        assert response.status_code == 404
    
    async def test_redirect_expired(self, client: AsyncClient, mock_db_session, test_link_dict):
        """Тест редиректа по истекшей ссылке"""
        mock_execute = AsyncMock()
        
        class MockLink:
            def __init__(self, link_dict):
                self.short_code = link_dict["short_code"]
                self.original_url = link_dict["original_url"]
                self.expires_at = datetime.utcnow() - timedelta(days=1)
                self.is_active = True
        
        mock_link = MockLink(test_link_dict)
        mock_execute.scalar_one_or_none = MagicMock(return_value=mock_link)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        mock_db_session.commit = AsyncMock()
        
        response = await client.get(f"/api/{test_link_dict['short_code']}")
        
        assert response.status_code == 410