import pytest
import asyncio
import sys
import os
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import uuid

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.security import create_access_token, get_password_hash
from app.core.config import settings


@pytest.fixture(autouse=True)
def patch_bcrypt():
    with patch('passlib.hash.bcrypt.hash') as mock_hash:
        mock_hash.return_value = "$2b$12$FakeHashForTesting"
        yield

@pytest.fixture
def mock_db_session():
    mock = AsyncMock()
    
    mock_execute = AsyncMock()
    mock_execute.scalar_one_or_none = MagicMock(return_value=None)
    mock_execute.scalars = MagicMock()
    mock_execute.scalars.return_value.first = MagicMock(return_value=None)
    mock_execute.scalars.return_value.all = MagicMock(return_value=[])
    
    mock.execute = AsyncMock(return_value=mock_execute)
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.close = AsyncMock()
    mock.refresh = AsyncMock()
    mock.add = MagicMock()
    
    return mock

@pytest.fixture
def mock_redis():
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.setex = AsyncMock()
    mock.delete = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    return mock

@pytest.fixture
def mock_cache_service():
    mock = AsyncMock()
    mock.get_redis = AsyncMock()
    mock.cache_link = AsyncMock()
    mock.get_cached_link = AsyncMock(return_value=None)
    mock.invalidate_cache = AsyncMock()
    mock.cache_popular_links = AsyncMock()
    mock.get_popular_links = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def test_user_dict():
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "test@example.com",
        "password_hash": "$2b$12$FakeHashForTesting",
        "created_at": datetime.utcnow().isoformat()
    }

@pytest.fixture
def test_user_obj(test_user_dict):
    class MockUser:
        def __init__(self, data):
            self.id = data["id"]
            self.email = data["email"]
            self.password_hash = data["password_hash"]
            self.created_at = data["created_at"]
            
        def verify_password(self, password):
            return password == "password123"
        
        def dict(self):
            return {
                "id": self.id,
                "email": self.email,
                "created_at": self.created_at
            }
    
    return MockUser(test_user_dict)

@pytest.fixture
def test_link_dict(test_user_dict):
    return {
        "id": "660e8400-e29b-41d4-a716-446655440000",
        "short_code": "test123",
        "original_url": "https://example.com",
        "user_id": test_user_dict["id"],
        "clicks": 0,
        "last_clicked_at": None,
        "expires_at": None,
        "is_custom": False,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }

@pytest.fixture
def test_link_obj(test_link_dict):
    class MockLink:
        def __init__(self, data):
            self.id = data["id"]
            self.short_code = data["short_code"]
            self.original_url = data["original_url"]
            self.user_id = data["user_id"]
            self.clicks = data["clicks"]
            self.last_clicked_at = data["last_clicked_at"]
            self.expires_at = data["expires_at"]
            self.is_custom = data["is_custom"]
            self.is_active = data["is_active"]
            self.created_at = data["created_at"]
            
        def dict(self):
            return {
                "id": self.id,
                "short_code": self.short_code,
                "original_url": self.original_url,
                "user_id": self.user_id,
                "clicks": self.clicks,
                "created_at": self.created_at
            }
    
    return MockLink(test_link_dict)

@pytest.fixture
def auth_token():
    return create_access_token(data={"sub": "550e8400-e29b-41d4-a716-446655440000"})

@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def client():
    from app.main import app as fastapi_app
    
    async with AsyncClient(app=fastapi_app, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def override_dependencies(mock_db_session, mock_cache_service, test_user_obj):
    from app.main import app as fastapi_app
    from app.core.database import get_db
    from app.api.dependencies import get_optional_user, get_current_user
    import app.api.endpoints.links
    
    async def mock_get_db():
        yield mock_db_session
    
    async def mock_get_optional_user():
        return None
    
    async def mock_get_current_user():
        return test_user_obj
    
    fastapi_app.dependency_overrides[get_db] = mock_get_db
    fastapi_app.dependency_overrides[get_optional_user] = mock_get_optional_user
    fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user
    
    app.api.endpoints.links.cache_service = mock_cache_service
    
    yield
    
    fastapi_app.dependency_overrides.clear()
    app.api.endpoints.links.cache_service = None