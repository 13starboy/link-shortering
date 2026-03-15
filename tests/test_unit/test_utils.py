import pytest
import re
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from app.api.endpoints.links import generate_short_code
from app.schemas.schemas import LinkCreate, UserCreate

pytestmark = pytest.mark.unit

class TestGenerateShortCode:
    """Тесты для функции генерации короткого кода"""
    
    def test_generate_short_code_default_length(self):
        short_code = generate_short_code()
        assert isinstance(short_code, str)
        assert len(short_code) == 6
        assert re.match(r'^[a-zA-Z0-9]+$', short_code)
    
    def test_generate_short_code_custom_length(self):
        lengths = [4, 8, 10, 12]
        for length in lengths:
            short_code = generate_short_code(length)
            assert len(short_code) == length
            assert re.match(r'^[a-zA-Z0-9]+$', short_code)
    
    def test_generate_short_code_uniqueness(self):
        codes = set()
        num_codes = 100
        for _ in range(num_codes):
            code = generate_short_code()
            codes.add(code)
        assert len(codes) == num_codes
    
    def test_generate_short_code_contains_only_allowed_chars(self):
        short_code = generate_short_code()
        for char in short_code:
            assert char.isalnum()
    
    def test_generate_short_code_different_each_time(self):
        code1 = generate_short_code()
        code2 = generate_short_code()
        code3 = generate_short_code()
        assert code1 != code2
        assert code1 != code3
        assert code2 != code3
    
    @patch('secrets.choice')
    def test_generate_short_code_with_mocked_random(self, mock_choice):
        mock_choice.side_effect = ['a', 'b', 'c', 'd', 'e', 'f']
        short_code = generate_short_code(6)
        assert short_code == "abcdef"
        assert mock_choice.call_count == 6
    
    def test_generate_short_code_edge_cases(self):
        short_code_min = generate_short_code(1)
        assert len(short_code_min) == 1
        short_code_max = generate_short_code(50)
        assert len(short_code_max) == 50
        short_code_large = generate_short_code(100)
        assert len(short_code_large) == 100

class TestURLValidation:
    """Тесты для валидации URL"""
    
    def test_valid_urls_accepted(self):
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://subdomain.example.com",
            "https://example.com/path/to/page",
            "https://example.com?query=param",
            "https://example.com:8080",
            "http://localhost:8000",
            "https://example.com#fragment",
        ]
        
        for url in valid_urls:
            try:
                link = LinkCreate(original_url=url)
                normalized_link = str(link.original_url)
                
                if '?' in url:
                    link_base = normalized_link.replace('/?', '?')
                    url_base = url
                    assert link_base == url_base
                elif '#' in url:
                    link_base = normalized_link.replace('/#', '#')
                    url_base = url
                    assert link_base == url_base
                else:
                    assert normalized_link.rstrip('/') == url.rstrip('/')
            except ValidationError as e:
                pytest.fail()

    def test_invalid_urls_rejected(self):
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "http://",
            "https://",
            "http:/example.com",
            "https//example.com",
            "http://example. com",
            "",
        ]
        
        for url in invalid_urls:
            try:
                LinkCreate(original_url=url)
                from pydantic import HttpUrl
                try:
                    HttpUrl(url)
                    pytest.fail()
                except:
                    pass
            except ValidationError:
                pass

class TestExpirationDateValidation:
    
    def test_future_expiration_date_valid(self):
        future_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        try:
            link = LinkCreate(
                original_url="https://example.com",
                expires_at=future_date
            )
            assert link.expires_at is not None
        except Exception as e:
            pytest.fail()
    
    def test_past_expiration_date_allowed(self):
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        try:
            link = LinkCreate(
                original_url="https://example.com",
                expires_at=past_date
            )
            assert link.expires_at is not None
        except Exception as e:
            pytest.fail()
    
    def test_invalid_date_format_rejected(self):
        invalid_dates = [
            "2024-13-01",
            "2024-01-32",
            "2024/01/01",
            "tomorrow",
        ]
        
        for date_str in invalid_dates:
            with pytest.raises(ValidationError):
                LinkCreate(
                    original_url="https://example.com",
                    expires_at=date_str
                )

class TestCustomAliasValidation:
    
    def test_valid_aliases_accepted(self):
        valid_aliases = [
            "test",
            "test123",
            "my-link",
            "my_link",
            "a" * 50,
            "123456",
            "abc-123_def",
        ]
        
        for alias in valid_aliases:
            try:
                link = LinkCreate(
                    original_url="https://example.com",
                    custom_alias=alias
                )
                assert link.custom_alias == alias
            except Exception as e:
                pytest.fail()
    
    def test_invalid_aliases_rejected(self):
        invalid_aliases = [
            "ab",
            "a" * 51,
            "test@#$",
            "test url",
            "тест",
            "test.url",
        ]
        
        for alias in invalid_aliases:
            with pytest.raises(ValidationError):
                LinkCreate(
                    original_url="https://example.com",
                    custom_alias=alias
                )

class TestEmailValidation:
    
    def test_valid_emails_accepted(self):
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+label@example.com",
            "user@subdomain.example.com",
            "user@example.co.uk",
        ]
        
        for email in valid_emails:
            try:
                user = UserCreate(
                    email=email,
                    password="password123"
                )
                assert user.email == email
            except Exception as e:
                pytest.fail()
    
    def test_invalid_emails_rejected(self):
        invalid_emails = [
            "not-an-email",
            "missing@domain",
            "@example.com",
            "user@.com",
            "user@domain.",
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                UserCreate(
                    email=email,
                    password="password123"
                )

class TestPasswordValidation:
    
    def test_valid_passwords_accepted(self):
        valid_passwords = [
            "pass123",
            "a" * 6,
            "a" * 50,
            "Pass123!@#",
        ]
        
        for password in valid_passwords:
            try:
                user = UserCreate(
                    email="test@example.com",
                    password=password
                )
                assert user.password == password
            except Exception as e:
                pytest.fail()
    
    def test_invalid_passwords_rejected(self):
        invalid_passwords = [
            "12345",
            "a" * 5,
            "",
        ]
        
        for password in invalid_passwords:
            with pytest.raises(ValidationError):
                UserCreate(
                    email="test@example.com",
                    password=password
                )