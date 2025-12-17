# backend/src/db/postgres_client.py
"""Async Postgres client using asyncpg for metadata storage."""

import asyncpg
import os
from typing import List, Dict, Any, Optional

class PostgresClientWrapper:
    """Async wrapper for Postgres database operations."""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Create connection pool."""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
        return self.pool

    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def execute(self, query: str, *args):
        """Execute a query without returning results."""
        pool = await self.connect()
        async with pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch multiple rows."""
        pool = await self.connect()
        async with pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]

    async def fetchrow(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch a single row."""
        pool = await self.connect()
        async with pool.acquire() as connection:
            row = await connection.fetchrow(query, *args)
            return dict(row) if row else None

    async def fetchval(self, query: str, *args):
        """Fetch a single value."""
        pool = await self.connect()
        async with pool.acquire() as connection:
            return await connection.fetchval(query, *args)

# Global instance
postgres_client = PostgresClientWrapper()
