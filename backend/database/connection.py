"""
Database Connection Manager
PostgreSQL connection pool with context manager support
"""
import os
from contextlib import contextmanager
from typing import Generator
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """Database connection pool manager"""

    _pool = None

    @classmethod
    def initialize_pool(cls):
        """Initialize connection pool"""
        if cls._pool is None:
            try:
                cls._pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=20,
                    host=os.getenv('PG_DB_HOST', 'localhost'),
                    port=int(os.getenv('PG_DB_PORT', 5435)),
                    database=os.getenv('PG_DB_NAME', 'postgres'),
                    user=os.getenv('PG_DB_ID', 'postgres'),
                    password=os.getenv('PG_DB_PW', ''),
                    options='-c search_path=saeum_ai_api,public'  # 스키마 설정
                )
                print("✅ Database connection pool initialized")
            except Exception as e:
                print(f"❌ Failed to initialize connection pool: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """Get connection from pool"""
        if cls._pool is None:
            cls.initialize_pool()
        return cls._pool.getconn()

    @classmethod
    def return_connection(cls, conn):
        """Return connection to pool"""
        if cls._pool:
            cls._pool.putconn(conn)

    @classmethod
    def close_all_connections(cls):
        """Close all connections in pool"""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            print("✅ All database connections closed")


@contextmanager
def get_db_connection() -> Generator:
    """
    Context manager for database connections

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM prompts")
            results = cursor.fetchall()
    """
    conn = None
    try:
        conn = DatabaseConnection.get_connection()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            DatabaseConnection.return_connection(conn)


@contextmanager
def get_db_cursor() -> Generator:
    """
    Context manager for database cursor with dict-like results

    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM prompts WHERE prompt_key = %s", (1,))
            result = cursor.fetchone()
            print(result['prompt_text'])
    """
    conn = None
    cursor = None
    try:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            DatabaseConnection.return_connection(conn)


# Initialize pool on module import
DatabaseConnection.initialize_pool()
