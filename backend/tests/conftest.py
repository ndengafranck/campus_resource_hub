import os
# Set mandatory config before importing the application; no connection is opened on import.
os.environ.setdefault('DATABASE_URL', 'sqlite+pysqlite:///:memory:')
os.environ.setdefault('JWT_SECRET', 'test-only-32-plus-characters-not-for-use-in-production')

from app.db import engine
from sqlalchemy import text

# SQLite is a lightweight substitute used only to exercise endpoint logic.
# PostgreSQL-specific schema creation, migration and performance require PostgreSQL tests.
with engine.begin() as conn:
    conn.execute(text("""CREATE TABLE IF NOT EXISTS app_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"""))
    conn.execute(text("""CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '', url TEXT NOT NULL, category TEXT NOT NULL,
        owner_id INTEGER NOT NULL REFERENCES app_users(id),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"""))
