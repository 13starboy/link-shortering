import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError

from app.api.middleware.auth import AuthMiddleware, verify_token

pytestmark = pytest.mark.unit

@pytest.fixture
def middleware():
    return AuthMiddleware()

@pytest.fixture
def mock_request():
    request = AsyncMock(spec=Request)
    request.state = MagicMock()
    request.state._mock_children = {}
    return request

@pytest.fixture
def mock_call_next():
    return AsyncMock(return_value="response")

class TestAuthMiddleware:
    """Тесты для middleware аутентификации"""
    
    async def test_auth_middleware_public_paths(self, middleware, mock_request, mock_call_next):
        public_paths = [
            "/api/register",
            "/api/login",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
        
        for path in public_paths:
            mock_request.url.path = path
            mock_request.headers = {}
            result = await middleware(mock_request, mock_call_next)
            assert result == "response"
            assert hasattr(mock_request.state, 'user')
            mock_call_next.assert_called_once_with(mock_request)
            mock_call_next.reset_mock()
    
    async def test_auth_middleware_no_auth_header(self, middleware, mock_request, mock_call_next):
        mock_request.url.path = "/api/links/shorten"
        mock_request.headers = {}
        
        result = await middleware(mock_request, mock_call_next)
        
        assert result == "response"
        assert hasattr(mock_request.state, 'user')
        mock_call_next.assert_called_once_with(mock_request)
    
    async def test_auth_middleware_with_valid_token(self, middleware, mock_request, mock_call_next):
        mock_request.url.path = "/api/links/shorten"
        mock_request.headers = {"Authorization": "Bearer valid.token"}
        
        with patch('app.api.middleware.auth.decode_access_token') as mock_decode:
            mock_decode.return_value = {"sub": "user123"}
            
            result = await middleware(mock_request, mock_call_next)
            
            assert result == "response"
            assert hasattr(mock_request.state, 'user')
            assert mock_request.state.user == "user123"
            mock_decode.assert_called_once_with("valid.token")
            mock_call_next.assert_called_once_with(mock_request)
    
    async def test_auth_middleware_with_invalid_token(self, middleware, mock_request, mock_call_next):
        mock_request.url.path = "/api/links/shorten"
        mock_request.headers = {"Authorization": "Bearer invalid.token"}
        
        if hasattr(mock_request.state, 'user'):
            delattr(mock_request.state, 'user')
        
        with patch('app.api.middleware.auth.decode_access_token') as mock_decode:
            mock_decode.return_value = None
            
            result = await middleware(mock_request, mock_call_next)
            
            assert result == "response"
            assert not hasattr(mock_request.state, 'user')
            mock_decode.assert_called_once_with("invalid.token")
            mock_call_next.assert_called_once_with(mock_request)
    
    async def test_auth_middleware_wrong_scheme(self, middleware, mock_request, mock_call_next):
        mock_request.url.path = "/api/links/shorten"
        mock_request.headers = {"Authorization": "Basic dXNlcjpwYXNz"}
        
        if hasattr(mock_request.state, 'user'):
            delattr(mock_request.state, 'user')
        
        result = await middleware(mock_request, mock_call_next)
        
        assert result == "response"
        assert not hasattr(mock_request.state, 'user')
        mock_call_next.assert_called_once_with(mock_request)

class TestVerifyToken:
    """Тесты для функции verify_token"""
    
    @pytest.fixture
    def mock_credentials(self):
        credentials = MagicMock(spec=HTTPAuthorizationCredentials)
        return credentials
    
    async def test_verify_token_valid(self, mock_credentials):
        mock_credentials.credentials = "valid.token"
        
        with patch('app.api.middleware.auth.decode_access_token') as mock_decode:
            mock_decode.return_value = {"sub": "user123"}
            
            result = await verify_token(mock_credentials)
            
            assert result == {"sub": "user123"}
            mock_decode.assert_called_once_with("valid.token")
    
    async def test_verify_token_invalid(self, mock_credentials):
        mock_credentials.credentials = "invalid.token"
        
        with patch('app.api.middleware.auth.decode_access_token') as mock_decode:
            mock_decode.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await verify_token(mock_credentials)
            
            assert exc_info.value.status_code == 401
