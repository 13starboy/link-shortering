#!/bin/bash
# entrypoint.sh

set -e


wait_for_postgres() {
    echo "Waiting for PostgreSQL..."
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
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'postgres'),
            port=os.getenv('DB_PORT', '5432'),
            user=os.getenv('DB_USER', 'urlshortener'),
            password=os.getenv('DB_PASSWORD', 'urlshortener123'),
            database=os.getenv('DB_NAME', 'urlshortener')
        )
        await conn.close()
        return True
    except:
        return False

if asyncio.run(check()):
    sys.exit(0)
else:
    sys.exit(1)
" 2>/dev/null; then
            echo "PostgreSQL is ready!"
            return 0
        fi
        
        echo "PostgreSQL not ready yet... ($((count+1))/$retries)"
        sleep 2
        count=$((count + 1))
    done
    
    echo "PostgreSQL failed to start"
    return 1
}


wait_for_redis() {
    echo "Waiting for Redis..."
    local retries=30
    local count=0
    
    while [ $count -lt $retries ]; do
        if python -c "
import redis
import os
import sys

try:
    r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
    r.ping()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null; then
            echo "Redis is ready!"
            return 0
        fi
        
        echo "Redis not ready yet... ($((count+1))/$retries)"
        sleep 2
        count=$((count + 1))
    done
    
    echo "Redis failed to start, continuing anyway..."
    return 0
}


wait_for_postgres
wait_for_redis

echo "Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "Migrations completed successfully"
else
    echo "Migrations failed"
    exit 1
fi


mkdir -p /app/logs

echo "Starting application server..."
exec "$@"