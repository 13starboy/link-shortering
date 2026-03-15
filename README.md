# URL Shortener API Documentation

Базовый URL: `https://link-shortering.onrender.com`

---

## Публичные эндпоинты (без авторизации)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/health` | Проверка работоспособности сервера |
| GET | `/` | Информация о сервисе |
| GET | `/api/{short_code}` | Редирект на оригинальный URL |
| POST | `/api/register` | Регистрация нового пользователя |
| POST | `/api/login` | Вход в систему (получение JWT токена) |

---

## Защищенные эндпоинты (требуют Bearer токен)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/links/shorten` | Создание короткой ссылки (с опциональным кастомным alias и временем жизни) |
| GET | `/api/links/{short_code}/stats` | Получение статистики по ссылке (клики, дата создания, последний переход) |
| PUT | `/api/links/{short_code}` | Обновление оригинального URL для существующей короткой ссылки |
| DELETE | `/api/links/{short_code}` | Удаление короткой ссылки |
| GET | `/api/links/search` | Поиск ссылок по оригинальному URL |
| GET | `/api/links/expired/history` | История истекших ссылок пользователя |

---
## Запуск (Docker)

docker-compose up --build

---
## База Данных
PostgreSQL 15 - основная база данных

Redis 7 - кэширование популярных ссылок

SQLAlchemy 2.0 - ORM для работы с БД

Alembic - миграции базы данных
---
deploy pic:
<img width="1514" height="801" alt="image" src="https://github.com/user-attachments/assets/f5d64a00-4f63-4d00-bc4e-02ca81d1a4d4" />

swagger urls info:
<img width="1794" height="1192" alt="image" src="https://github.com/user-attachments/assets/1d6bc59d-7714-4bc1-9d02-be12909031a9" />

--
## Тестирование
для запуска тестов
```
pip install -r requirements.txt

pytest tests -v
```

для получения отчета
```
coverage run -m pytest tests
```
для просмотра в консоле:
```
coverage report
```
для генерации html отчета
```
coverage html
```
--
## Результаты
```
(venv) PS C:\project\link-shortering> coverage run -m pytest tests
================================================= test session starts =================================================
platform win32 -- Python 3.11.9, pytest-7.4.3, pluggy-1.6.0 -- C:\project\link-shortering\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\project\link-shortering
configfile: pytest.ini
plugins: anyio-3.7.1, asyncio-0.21.1, cov-4.1.0, env-1.1.1, mock-3.12.0
asyncio: mode=Mode.AUTO
collected 119 items

tests/test_functional/test_auth.py::TestAuth::test_register_success PASSED                                       [  0%]
tests/test_functional/test_auth.py::TestAuth::test_register_duplicate_email PASSED                               [  1%]
tests/test_functional/test_auth.py::TestAuth::test_login_success PASSED                                          [  2%]
tests/test_functional/test_auth.py::TestAuth::test_login_wrong_password PASSED                                   [  3%]
tests/test_functional/test_links.py::TestLinks::test_create_link_unauthorized PASSED                             [  4%]
tests/test_functional/test_links.py::TestLinks::test_create_link_authorized PASSED                               [  5%]
tests/test_functional/test_links.py::TestLinks::test_create_custom_link PASSED                                   [  5%]
tests/test_functional/test_links.py::TestLinks::test_create_duplicate_custom_link PASSED                         [  6%]
tests/test_functional/test_links.py::TestLinks::test_create_link_with_expiration PASSED                          [  7%]
tests/test_functional/test_links.py::TestLinks::test_get_link_stats PASSED                                       [  8%]
tests/test_functional/test_links.py::TestLinks::test_get_stats_unauthorized PASSED                               [  9%]
tests/test_functional/test_links.py::TestLinks::test_update_link PASSED                                          [ 10%]
tests/test_functional/test_links.py::TestLinks::test_update_nonexistent_link PASSED                              [ 10%]
tests/test_functional/test_links.py::TestLinks::test_delete_link PASSED                                          [ 11%]
tests/test_functional/test_links.py::TestLinks::test_delete_nonexistent_link PASSED                              [ 12%]
tests/test_functional/test_links.py::TestLinks::test_search_links PASSED                                         [ 13%]
tests/test_functional/test_links.py::TestLinks::test_search_without_auth PASSED                                  [ 14%]
tests/test_functional/test_redirect.py::TestRedirect::test_redirect_success PASSED                               [ 15%]
tests/test_functional/test_redirect.py::TestRedirect::test_redirect_nonexistent PASSED                           [ 15%]
tests/test_functional/test_redirect.py::TestRedirect::test_redirect_expired PASSED                               [ 16%]
tests/test_functional/test_validation.py::TestValidation::test_create_link_invalid_url PASSED                    [ 17%]
tests/test_functional/test_validation.py::TestValidation::test_create_link_missing_url PASSED                    [ 18%]
tests/test_functional/test_validation.py::TestValidation::test_custom_alias_too_short PASSED                     [ 19%]
tests/test_functional/test_validation.py::TestValidation::test_custom_alias_too_long PASSED                      [ 20%]
tests/test_functional/test_validation.py::TestValidation::test_custom_alias_invalid_chars PASSED                 [ 21%]
tests/test_functional/test_validation.py::TestValidation::test_invalid_expires_at_format PASSED                  [ 21%]
tests/test_integration/test_cache.py::TestCacheIntegration::test_cache_fallback_on_redis_failure PASSED          [ 22%]
tests/test_unit/test_auth_middleware.py::TestAuthMiddleware::test_auth_middleware_public_paths PASSED            [ 23%]
tests/test_unit/test_auth_middleware.py::TestAuthMiddleware::test_auth_middleware_no_auth_header PASSED          [ 24%]
tests/test_unit/test_auth_middleware.py::TestAuthMiddleware::test_auth_middleware_with_valid_token PASSED        [ 25%]
tests/test_unit/test_auth_middleware.py::TestAuthMiddleware::test_auth_middleware_with_invalid_token PASSED      [ 26%]
tests/test_unit/test_auth_middleware.py::TestAuthMiddleware::test_auth_middleware_wrong_scheme PASSED            [ 26%]
tests/test_unit/test_auth_middleware.py::TestVerifyToken::test_verify_token_valid PASSED                         [ 27%]
tests/test_unit/test_auth_middleware.py::TestVerifyToken::test_verify_token_invalid PASSED                       [ 28%]
tests/test_unit/test_cache_service.py::TestCacheService::test_get_redis_success PASSED                           [ 29%]
tests/test_unit/test_cache_service.py::TestCacheService::test_get_redis_failure_fallback PASSED                  [ 30%]
tests/test_unit/test_cache_service.py::TestCacheService::test_cache_link_with_redis PASSED                       [ 31%]
tests/test_unit/test_cache_service.py::TestCacheService::test_cache_link_without_redis PASSED                    [ 31%]
tests/test_unit/test_cache_service.py::TestCacheService::test_get_cached_link_with_redis PASSED                  [ 32%]
tests/test_unit/test_cache_service.py::TestCacheService::test_get_cached_link_from_memory PASSED                 [ 33%]
tests/test_unit/test_cache_service.py::TestCacheService::test_get_cached_link_expired PASSED                     [ 34%]
tests/test_unit/test_cache_service.py::TestCacheService::test_invalidate_cache_with_redis PASSED                 [ 35%]
tests/test_unit/test_cache_service.py::TestCacheService::test_invalidate_cache_without_redis PASSED              [ 36%]
tests/test_unit/test_cache_service.py::TestCacheService::test_cache_popular_links PASSED                         [ 36%]
tests/test_unit/test_cache_service.py::TestCacheService::test_get_popular_links PASSED                           [ 37%]
tests/test_unit/test_database.py::TestDatabase::test_get_db PASSED                                               [ 38%]
tests/test_unit/test_database.py::TestDatabase::test_get_db_closes_session PASSED                                [ 39%]
tests/test_unit/test_database.py::TestDatabase::test_engine_creation PASSED                                      [ 40%]
tests/test_unit/test_database.py::TestDatabase::test_session_local_creation PASSED                               [ 41%]
tests/test_unit/test_dependencies.py::TestDependencies::test_get_current_user_success PASSED                     [ 42%]
tests/test_unit/test_dependencies.py::TestDependencies::test_get_current_user_invalid_token PASSED               [ 42%]
tests/test_unit/test_dependencies.py::TestDependencies::test_get_current_user_user_not_found PASSED              [ 43%]
tests/test_unit/test_dependencies.py::TestDependencies::test_get_current_user_no_sub_in_token PASSED             [ 44%]
tests/test_unit/test_dependencies.py::TestDependencies::test_get_optional_user_with_token PASSED                 [ 45%]
tests/test_unit/test_dependencies.py::TestDependencies::test_get_optional_user_no_token PASSED                   [ 46%]
tests/test_unit/test_dependencies.py::TestDependencies::test_get_optional_user_invalid_token PASSED              [ 47%]
tests/test_unit/test_models.py::TestUserModel::test_user_creation PASSED                                         [ 47%]
tests/test_unit/test_models.py::TestUserModel::test_user_attributes PASSED                                       [ 48%]
tests/test_unit/test_models.py::TestLinkModel::test_link_creation PASSED                                         [ 49%]
tests/test_unit/test_models.py::TestLinkModel::test_link_expiration PASSED                                       [ 50%]
tests/test_unit/test_models.py::TestLinkModel::test_increment_clicks PASSED                                      [ 51%]
tests/test_unit/test_models.py::TestLinkModel::test_link_attributes PASSED                                       [ 52%]
tests/test_unit/test_security.py::TestPasswordHashing::test_password_hash_success PASSED                         [ 52%]
tests/test_unit/test_security.py::TestPasswordHashing::test_password_hash_empty PASSED                           [ 53%]
tests/test_unit/test_security.py::TestPasswordHashing::test_password_hash_long PASSED                            [ 54%]
tests/test_unit/test_security.py::TestPasswordHashing::test_password_hash_spec_chars PASSED                      [ 55%]
tests/test_unit/test_security.py::TestPasswordHashing::test_password_verification_success PASSED                 [ 56%]
tests/test_unit/test_security.py::TestPasswordHashing::test_password_verification_failure PASSED                 [ 57%]
tests/test_unit/test_security.py::TestPasswordHashing::test_password_verification_empty PASSED                   [ 57%]
tests/test_unit/test_security.py::TestPasswordHashing::test_password_verification_invalid_hash PASSED            [ 58%]
tests/test_unit/test_security.py::TestPasswordHashing::test_different_hashes_for_same_password PASSED            [ 59%]
tests/test_unit/test_security.py::TestPasswordHashing::test_password_hash_consistency PASSED                     [ 60%]
tests/test_unit/test_security.py::TestPasswordHashing::test_password_hash_with_unicode PASSED                    [ 61%]
tests/test_unit/test_security.py::TestJWT::test_create_access_token_success PASSED                               [ 62%]
tests/test_unit/test_security.py::TestJWT::test_create_access_token_without_sub PASSED                           [ 63%]
tests/test_unit/test_security.py::TestJWT::test_create_access_token_with_custom_expiry PASSED                    [ 63%]
tests/test_unit/test_security.py::TestJWT::test_create_access_token_with_long_expiry PASSED                      [ 64%]
tests/test_unit/test_security.py::TestJWT::test_create_access_token_with_empty_data PASSED                       [ 65%]
tests/test_unit/test_security.py::TestJWT::test_decode_valid_token PASSED                                        [ 66%]
tests/test_unit/test_security.py::TestJWT::test_decode_token_without_sub PASSED                                  [ 67%]
tests/test_unit/test_security.py::TestJWT::test_decode_invalid_token PASSED                                      [ 68%]
tests/test_unit/test_security.py::TestJWT::test_decode_empty_token PASSED                                        [ 68%]
tests/test_unit/test_security.py::TestJWT::test_decode_malformed_token PASSED                                    [ 69%]
tests/test_unit/test_security.py::TestJWT::test_token_expiration PASSED                                          [ 70%]
tests/test_unit/test_security.py::TestJWT::test_token_from_different_secret PASSED                               [ 71%]
tests/test_unit/test_security.py::TestJWT::test_token_without_expiration PASSED                                  [ 72%]
tests/test_unit/test_security.py::TestJWT::test_token_with_future_expiration PASSED                              [ 73%]
tests/test_unit/test_security.py::TestJWT::test_token_with_past_expiration PASSED                                [ 73%]
tests/test_unit/test_security.py::TestJWT::test_token_with_additional_claims PASSED                              [ 74%]
tests/test_unit/test_security.py::TestJWT::test_token_with_numeric_data PASSED                                   [ 75%]
tests/test_unit/test_security.py::TestJWT::test_multiple_tokens_different PASSED                                 [ 76%]
tests/test_unit/test_security.py::TestJWT::test_token_algorithm PASSED                                           [ 77%]
tests/test_unit/test_security.py::TestPasswordHashingEdgeCases::test_password_hash_with_mocked_context PASSED    [ 78%]
tests/test_unit/test_security.py::TestPasswordHashingEdgeCases::test_password_verification_with_none PASSED      [ 78%]
tests/test_unit/test_security.py::TestJWTEdgeCases::test_decode_access_token_with_empty_string PASSED            [ 79%]
tests/test_unit/test_security.py::TestJWTEdgeCases::test_create_access_token_with_none_data PASSED               [ 80%]
tests/test_unit/test_security.py::TestJWTEdgeCases::test_create_access_token_with_invalid_data PASSED            [ 81%]
tests/test_unit/test_security.py::TestJWTEdgeCases::test_token_with_custom_headers PASSED                        [ 82%]
tests/test_unit/test_security.py::TestJWTEdgeCases::test_create_access_token_exception_handling PASSED           [ 83%]
tests/test_unit/test_security.py::TestJWTEdgeCases::test_decode_access_token_with_expired_signature PASSED       [ 84%]
tests/test_unit/test_security.py::TestJWTEdgeCases::test_decode_access_token_with_wrong_algorithm PASSED         [ 84%]
tests/test_unit/test_utils.py::TestGenerateShortCode::test_generate_short_code_default_length PASSED             [ 85%]
tests/test_unit/test_utils.py::TestGenerateShortCode::test_generate_short_code_custom_length PASSED              [ 86%]
tests/test_unit/test_utils.py::TestGenerateShortCode::test_generate_short_code_uniqueness PASSED                 [ 87%]
tests/test_unit/test_utils.py::TestGenerateShortCode::test_generate_short_code_contains_only_allowed_chars PASSED [ 88%]
tests/test_unit/test_utils.py::TestGenerateShortCode::test_generate_short_code_different_each_time PASSED        [ 89%]
tests/test_unit/test_utils.py::TestGenerateShortCode::test_generate_short_code_with_mocked_random PASSED         [ 89%]
tests/test_unit/test_utils.py::TestGenerateShortCode::test_generate_short_code_edge_cases PASSED                 [ 90%]
tests/test_unit/test_utils.py::TestURLValidation::test_valid_urls_accepted PASSED                                [ 91%]
tests/test_unit/test_utils.py::TestURLValidation::test_invalid_urls_rejected PASSED                              [ 92%]
tests/test_unit/test_utils.py::TestExpirationDateValidation::test_future_expiration_date_valid PASSED            [ 93%]
tests/test_unit/test_utils.py::TestExpirationDateValidation::test_past_expiration_date_allowed PASSED            [ 94%]
tests/test_unit/test_utils.py::TestExpirationDateValidation::test_invalid_date_format_rejected PASSED            [ 94%]
tests/test_unit/test_utils.py::TestCustomAliasValidation::test_valid_aliases_accepted PASSED                     [ 95%]
tests/test_unit/test_utils.py::TestCustomAliasValidation::test_invalid_aliases_rejected PASSED                   [ 96%]
tests/test_unit/test_utils.py::TestEmailValidation::test_valid_emails_accepted PASSED                            [ 97%]
tests/test_unit/test_utils.py::TestEmailValidation::test_invalid_emails_rejected PASSED                          [ 98%]
tests/test_unit/test_utils.py::TestPasswordValidation::test_valid_passwords_accepted PASSED                      [ 99%]
tests/test_unit/test_utils.py::TestPasswordValidation::test_invalid_passwords_rejected PASSED                    [100%]
```
================================================= 119 passed in 4.35s =================================================

### Детальный отчет по модулям:


| Модуль | Файл | Покрытие |
|--------|------|----------|
| **API** | `app/api/dependencies.py` | 97% |
| **API** | `app/api/endpoints/auth.py` | 100% |
| **API** | `app/api/endpoints/links.py` | 92% |
| **API** | `app/api/middleware/auth.py` | 93% |
| **Core** | `app/core/config.py` | 100% |
| **Core** | `app/core/database.py` | 100% |
| **Core** | `app/core/security.py` | 100% |
| **Main** | `app/main.py` | 74% |
| **Models** | `app/models/models.py` | 100% |
| **Schemas** | `app/schemas/schemas.py` | 100% |
| **Services** | `app/services/cache_service.py` | 93% |
| **ИТОГО** | **Все модули** | **95%** |

