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
