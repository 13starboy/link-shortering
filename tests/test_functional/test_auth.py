import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from jose import jwt

pytestmark = pytest.mark.functional

class TestAuth:
    
    async def test_register_success(self, client: AsyncClient, mock_db_session):
        """Тест успешной регистрации"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        mock_db_session.commit = AsyncMock()
        
        async def mock_refresh(user):
            user.id = "550e8400-e29b-41d4-a716-446655440000"
            user.created_at = datetime.utcnow().isoformat()
        
        mock_db_session.refresh = AsyncMock(side_effect=mock_refresh)
        
        with patch('app.api.endpoints.auth.get_password_hash') as mock_hash:
            mock_hash.return_value = "$2b$12$FakeHashForTesting"
            
            response = await client.post("/api/register", json={
                "email": "newuser@example.com",
                "password": "password123"
            })
            
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == "newuser@example.com"
            assert "id" in data
            assert data["id"] is not None
    
    async def test_register_duplicate_email(self, client: AsyncClient, mock_db_session, test_user_dict):
        """Тест регистрации с существующим email"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=test_user_dict)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        response = await client.post("/api/register", json={
            "email": test_user_dict["email"],
            "password": "password123"
        })
        
        assert response.status_code == 400
    
    async def test_login_success(self, client: AsyncClient, mock_db_session, test_user_obj):
        """Тест успешного входа"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=test_user_obj)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        with patch('app.api.endpoints.auth.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            response = await client.post("/api/login", json={
                "email": "test@example.com",
                "password": "password123"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
    
    async def test_login_wrong_password(self, client: AsyncClient, mock_db_session, test_user_obj):
        """Тест входа с неверным паролем"""
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=test_user_obj)
        mock_db_session.execute = AsyncMock(return_value=mock_execute)
        
        with patch('app.api.endpoints.auth.verify_password') as mock_verify:
            mock_verify.return_value = False
            
            response = await client.post("/api/login", json={
                "email": "test@example.com",
                "password": "wrongpassword"
            })
            
            assert response.status_code == 401