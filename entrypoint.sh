#!/bin/bash
# entrypoint.sh

set -e

echo "========================================"
echo "URL Shortener Service - Starting on Render"
echo "========================================"
echo "PORT: $PORT"
echo "DATABASE_URL: ${DATABASE_URL//:[^@]*/@***}"  # Скрываем пароль
echo "========================================"

# Функция ожидания PostgreSQL
wait_for_postgres() {
    echo "⏳ Waiting for PostgreSQL..."
    local retries=30
    local count=0
    
    while [ $count -lt $retries ]; do
        if python -c "
import asyncio
import asyncpg
import os
import sys

async def check():
    try:
        # Render предоставляет DATABASE_URL
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            # Убираем +asyncpg если есть
            db_url = db_url.replace('+asyncpg', '')
            conn = await asyncpg.connect(db_url)
            await conn.close()
            return True
    except Exception as e:
        print(f'Connection error: {e}', file=sys.stderr)
        return False

if asyncio.run(check()):
    sys.exit(0)
else:
    sys.exit(1)
" 2>/dev/null; then
            echo "✅ PostgreSQL is ready!"
            return 0
        fi
        
        echo "⏳ PostgreSQL not ready yet... ($((count+1))/$retries)"
        sleep 2
        count=$((count + 1))
    done
    
    echo "❌ PostgreSQL failed to start after $retries attempts"
    echo "Please check your DATABASE_URL in Render dashboard"
    return 1
}


wait_for_postgres || {
    echo "❌ Cannot continue without PostgreSQL"
    exit 1
}


echo "🔄 Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migrations failed"
    echo "Checking migration history..."
    alembic history
    exit 1
fi


mkdir -p /app/logs

echo "🚀 Starting application server on port $PORT..."
exec "$@"