import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from jose import JWTError
from fastapi import HTTPException, status

from app.api.dependencies import get_current_user, get_optional_user
from app.core.security import create_access_token

pytestmark = pytest.mark.unit

class TestDependencies:
    
    async def test_get_current_user_success(self):
        from app.api.dependencies import get_current_user
        from app.core.security import create_access_token
        
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token(data={"sub": user_id})
        
        mock_db = AsyncMock()
        mock_execute = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_execute.scalar_one_or_none = MagicMock(return_value=mock_user)
        mock_db.execute = AsyncMock(return_value=mock_execute)
        
        result = await get_current_user(token=token, db=mock_db)
        
        assert result is not None
        assert result.id == user_id
    
    async def test_get_current_user_invalid_token(self):
        from app.api.dependencies import get_current_user
        
        mock_db = AsyncMock()
        invalid_token = "invalid.token.string"
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=invalid_token, db=mock_db)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_get_current_user_user_not_found(self):
        from app.api.dependencies import get_current_user
        from app.core.security import create_access_token
        
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token(data={"sub": user_id})
        
        mock_db = AsyncMock()
        mock_execute = AsyncMock()
        mock_execute.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_execute)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=mock_db)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_get_current_user_no_sub_in_token(self):
        from app.api.dependencies import get_current_user
        from app.core.security import create_access_token
        
        token = create_access_token(data={"other": "value"})
        
        mock_db = AsyncMock()
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=mock_db)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_get_optional_user_with_token(self):
        from app.api.dependencies import get_optional_user
        from app.core.security import create_access_token
        
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        token = create_access_token(data={"sub": user_id})
        
        mock_db = AsyncMock()
        mock_execute = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_execute.scalar_one_or_none = MagicMock(return_value=mock_user)
        mock_db.execute = AsyncMock(return_value=mock_execute)
        
        result = await get_optional_user(token=token, db=mock_db)
        
        assert result is not None
        assert result.id == user_id
    
    async def test_get_optional_user_no_token(self):
        from app.api.dependencies import get_optional_user
        
        mock_db = AsyncMock()
        
        result = await get_optional_user(token=None, db=mock_db)
        
        assert result is None
    
    async def test_get_optional_user_invalid_token(self):
        from app.api.dependencies import get_optional_user
        
        mock_db = AsyncMock()
        invalid_token = "invalid.token.string"
        
        result = await get_optional_user(token=invalid_token, db=mock_db)
        
        assert result is None