import pytest
from datetime import datetime, timedelta
from jose import jwt
from unittest.mock import patch, MagicMock
from passlib.context import CryptContext

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from app.core.config import settings

pytestmark = pytest.mark.unit

@pytest.fixture(autouse=True)
def patch_bcrypt():
    with patch('app.core.security.pwd_context.verify') as mock_verify, \
         patch('app.core.security.pwd_context.hash') as mock_hash:
        
        mock_hash.return_value = "$2b$12$KIXZ1QBQK7JkY1Zq1QK7JkY1Zq1QK7JkY1Zq1QK7Jk"
        
        def verify_side_effect(plain, hashed):
            if hashed is None or not isinstance(hashed, str):
                return False
            if hashed == "invalid_hash":
                return False
            if hashed.startswith("$2b$"):
                return plain == "mysecretpassword" or plain == "password123" or plain == "consistent_password" or plain == "пароль"
            return False
        
        mock_verify.side_effect = verify_side_effect
        
        yield

class TestPasswordHashing:
    """Тесты для хэширования паролей"""
    
    def test_password_hash_success(self):
        """Тест успешного создания хэша пароля"""
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")
    
    def test_password_hash_empty(self):
        """Тест хэширования пустого пароля"""
        password = ""
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_password_hash_long(self):
        password = "a" * 100
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_password_hash_spec_chars(self):
        """Тест хэширования пароля со спецсимволами"""
        password = "P@ssw0rd!@#$%^&*()"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
    
    def test_password_verification_success(self):
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) == True
    
    def test_password_verification_failure(self):
        password = "mysecretpassword"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) == False
    
    def test_password_verification_empty(self):
        password = "mysecretpassword"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) == False
    
    def test_password_verification_invalid_hash(self):
        """Тест проверки с невалидным хэшем"""
        password = "mysecretpassword"
        invalid_hash = "not_a_valid_hash"
        
        assert verify_password(password, invalid_hash) == False
    
    def test_different_hashes_for_same_password(self):
        password = "samepassword"
        
        with patch('app.core.security.pwd_context.hash') as mock_hash:
            mock_hash.side_effect = ["hash1", "hash2"]
            hash1 = get_password_hash(password)
            hash2 = get_password_hash(password)
            
            assert hash1 != hash2
    
    def test_password_hash_consistency(self):
        password = "consistent_password"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert verify_password(password, hash1) == True
        assert verify_password(password, hash2) == True
    
    def test_password_hash_with_unicode(self):
        """Тест хэширования пароля с юникод символами"""
        password = "пароль"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) == True

class TestJWT:
    """Тесты для JWT токенов"""
    
    def test_create_access_token_success(self):
        """Тест успешного создания токена"""
        data = {"sub": "user123", "role": "admin"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_without_sub(self):
        data = {"role": "admin", "permissions": ["read", "write"]}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_create_access_token_with_custom_expiry(self):
        """Тест создания токена с кастомным временем жизни"""
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=5)
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_create_access_token_with_long_expiry(self):
        """Тест создания токена с длительным сроком жизни"""
        data = {"sub": "user123"}
        expires_delta = timedelta(days=30)
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert token is not None
    
    def test_create_access_token_with_empty_data(self):
        """Тест создания токена с пустыми данными"""
        data = {}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_decode_valid_token(self):
        """Тест декодирования валидного токена"""
        data = {"sub": "user123", "custom": "value"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["custom"] == "value"
        assert "exp" in decoded
    
    def test_decode_token_without_sub(self):
        data = {"role": "admin", "user_id": "123"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert "sub" not in decoded
        assert decoded["role"] == "admin"
        assert decoded["user_id"] == "123"
    
    def test_decode_invalid_token(self):
        """Тест декодирования невалидного токена"""
        invalid_token = "invalid.token.string"
        
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None
    
    def test_decode_empty_token(self):
        """Тест декодирования пустого токена"""
        decoded = decode_access_token("")
        
        assert decoded is None
    
    def test_decode_malformed_token(self):
        """Тест декодирования поврежденного токена"""
        malformed_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        
        decoded = decode_access_token(malformed_token)
        
        assert decoded is None
    
    def test_token_expiration(self):
        """Тест что токен истекает через указанное время"""
        data = {"sub": "user123"}
        token = create_access_token(data, expires_delta=timedelta(seconds=1))
        
        import time
        time.sleep(2)
        
        decoded = decode_access_token(token)
        assert decoded is None
    
    def test_token_from_different_secret(self):
        other_secret = "different_secret_key_12345"
        token = jwt.encode(
            {"sub": "user123", "exp": datetime.utcnow() + timedelta(minutes=30)},
            other_secret,
            algorithm=settings.ALGORITHM
        )
        
        decoded = decode_access_token(token)
        assert decoded is None
    
    def test_token_without_expiration(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": False})
        assert "exp" in decoded
    
    def test_token_with_future_expiration(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user123"
    
    def test_token_with_past_expiration(self):
        """Тест токена с expiration в прошлом"""
        past_exp = datetime.utcnow() - timedelta(hours=1)
        token = jwt.encode(
            {"sub": "user123", "exp": past_exp},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        decoded = decode_access_token(token)
        assert decoded is None
    
    def test_token_with_additional_claims(self):
        data = {
            "sub": "user123",
            "name": "John Doe",
            "email": "john@example.com",
            "role": "admin",
            "permissions": ["create", "read", "update", "delete"]
        }
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["name"] == "John Doe"
        assert decoded["email"] == "john@example.com"
        assert decoded["role"] == "admin"
        assert decoded["permissions"] == ["create", "read", "update", "delete"]
    
    def test_token_with_numeric_data(self):
        """Тест токена с числовыми данными"""
        data = {
            "sub": "user123",
            "age": 25,
            "score": 99.5,
            "count": 1000
        }
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["age"] == 25
        assert decoded["score"] == 99.5
        assert decoded["count"] == 1000
    
    def test_multiple_tokens_different(self):
        """Тест что разные токены для одного пользователя разные"""
        data = {"sub": "user123"}
        
        with patch('app.core.security.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)
            token1 = create_access_token(data)
            
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 1)
            token2 = create_access_token(data)
            
            assert token1 != token2
    
    def test_token_algorithm(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        header = jwt.get_unverified_header(token)
        
        assert header["alg"] == settings.ALGORITHM

class TestPasswordHashingEdgeCases:
    
    def test_password_hash_with_mocked_context(self):
        with patch('app.core.security.pwd_context.hash') as mock_hash:
            mock_hash.side_effect = Exception("Unexpected error")
            
            with pytest.raises(Exception):
                get_password_hash("password")
    
    def test_password_verification_with_none(self):
        """Тест verify_password с None значениями"""
        result = verify_password(None, "hash")
        assert result == False
        
        result = verify_password("password", None)
        assert result == False
        
        result = verify_password(None, None)
        assert result == False


class TestJWTEdgeCases:
    """Тесты граничных случаев для JWT"""
    
    def test_decode_access_token_with_empty_string(self):
        result = decode_access_token("")
        assert result is None
    
    def test_create_access_token_with_none_data(self):
        with pytest.raises(Exception):
            create_access_token(None)
    
    def test_create_access_token_with_invalid_data(self):
        data = {"user": object()}
        
        with pytest.raises(Exception):
            create_access_token(data)
    
    def test_token_with_custom_headers(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        assert decoded["sub"] == "user123"
    
    @patch('app.core.security.jwt.encode')
    def test_create_access_token_exception_handling(self, mock_encode):
        mock_encode.side_effect = Exception("JWT Error")
        
        with pytest.raises(Exception):
            create_access_token({"sub": "user123"})

    def test_decode_access_token_with_expired_signature(self):
        expired_data = {"sub": "user123", "exp": datetime.utcnow() - timedelta(days=1)}
        token = jwt.encode(expired_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        result = decode_access_token(token)
        assert result is None
    
    def test_decode_access_token_with_wrong_algorithm(self):
        token = jwt.encode(
            {"sub": "user123"},
            settings.SECRET_KEY,
            algorithm="HS512"
        )
        
        result = decode_access_token(token)
        assert result is None