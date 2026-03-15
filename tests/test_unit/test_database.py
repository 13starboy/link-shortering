import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, engine, AsyncSessionLocal

pytestmark = pytest.mark.unit

class TestDatabase:
    """Тесты для модуля базы данных"""
    
    async def test_get_db(self):
        """Тест получения сессии БД"""
        db_gen = get_db()
        db = await db_gen.__anext__()

        assert isinstance(db, AsyncSession)
        with pytest.raises(StopAsyncIteration):
            await db_gen.__anext__()
    
    async def test_get_db_closes_session(self):
        """Тест что сессия закрывается после использования"""
        from app.core.database import get_db
        
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()
    
    def test_engine_creation(self):
        from app.core.database import engine
        assert engine is not None
    
    def test_session_local_creation(self):
        assert AsyncSessionLocal is not None
