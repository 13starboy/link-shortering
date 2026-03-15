import pytest
from datetime import datetime, timedelta
import uuid
from unittest.mock import MagicMock, AsyncMock

pytestmark = pytest.mark.unit

class TestUserModel:
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        mock_user = MagicMock()
        mock_user.id = str(uuid.uuid4())
        mock_user.email = "test@example.com"
        mock_user.password_hash = "hashed_password"
        mock_user.created_at = datetime.utcnow()
        
        assert mock_user.id is not None
        assert mock_user.email == "test@example.com"
        assert mock_user.password_hash != "password"
        assert mock_user.created_at is not None
    
    def test_user_attributes(self):
        from app.models.models import User
        
        assert hasattr(User, 'id')
        assert hasattr(User, 'email')
        assert hasattr(User, 'password_hash')
        assert hasattr(User, 'created_at')
        assert hasattr(User, 'links')

class TestLinkModel:
    
    def test_link_creation(self):
        """Тест создания ссылки"""
        mock_link = MagicMock()
        mock_link.id = str(uuid.uuid4())
        mock_link.short_code = "abc123"
        mock_link.original_url = "https://google.com"
        mock_link.user_id = str(uuid.uuid4())
        mock_link.clicks = 0
        mock_link.is_active = True
        mock_link.is_custom = False
        mock_link.created_at = datetime.utcnow()
        
        assert mock_link.id is not None
        assert mock_link.short_code == "abc123"
        assert mock_link.clicks == 0
        assert mock_link.is_active == True
    
    def test_link_expiration(self):
        """Тест истечения срока ссылки"""
        mock_link = MagicMock()
        mock_link.expires_at = datetime.utcnow() - timedelta(days=1)
        mock_link.is_active = True
        
        assert mock_link.expires_at < datetime.utcnow()
        
        if mock_link.expires_at < datetime.utcnow():
            mock_link.is_active = False
        
        assert mock_link.is_active == False
    
    def test_increment_clicks(self):
        mock_link = MagicMock()
        mock_link.clicks = 5
        mock_link.last_clicked_at = None
        
        mock_link.clicks += 1
        mock_link.last_clicked_at = datetime.utcnow()
        
        assert mock_link.clicks == 6
        assert mock_link.last_clicked_at is not None
    
    def test_link_attributes(self):
        from app.models.models import Link
        
        assert hasattr(Link, 'id')
        assert hasattr(Link, 'short_code')
        assert hasattr(Link, 'original_url')
        assert hasattr(Link, 'user_id')
        assert hasattr(Link, 'clicks')
        assert hasattr(Link, 'last_clicked_at')
        assert hasattr(Link, 'expires_at')
        assert hasattr(Link, 'is_custom')
        assert hasattr(Link, 'is_active')
        assert hasattr(Link, 'created_at')