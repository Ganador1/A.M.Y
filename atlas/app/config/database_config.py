"""
Database Configuration Module
Provides database connection and configuration settings
"""

import os
from typing import Optional, Dict, Any
from urllib.parse import quote_plus
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
import asyncio
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

# Database Models Base
Base = declarative_base()

class DatabaseConfig:
    """Database configuration manager"""

    def __init__(self):
        self.database_url: Optional[str] = None
        self.engine = None
        self.SessionLocal = None
        self.metadata = MetaData()

    def get_database_url(self) -> str:
        """Get database URL from environment or use default SQLite"""
        if self.database_url:
            return self.database_url

        # Use Settings if available; fallback to SQLite dev DB
        db_url = getattr(settings, 'database_url', None)
        if db_url:
            self.database_url = db_url
            return db_url

        # Fallback to environment variables (optional) if Settings not populated
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "atlas")
        db_user = os.getenv("DB_USER", "atlas")
        db_password = os.getenv("DB_PASSWORD", "")

        if db_password:
            encoded_password = quote_plus(db_password)
            self.database_url = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
        else:
            self.database_url = "sqlite:///./atlas_dev.db"

        return self.database_url

    def create_engine(self, **kwargs):
        """Create database engine"""
        database_url = self.get_database_url()

        echo_env = os.getenv("DB_ECHO", "false").lower() == "true"
        engine_kwargs = {
            "echo": getattr(settings, 'db_echo', echo_env),
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }

        if "sqlite" in database_url:
            engine_kwargs.update({
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False}
            })

        engine_kwargs.update(kwargs)

        self.engine = create_engine(database_url, **engine_kwargs)
        return self.engine

    def create_session_local(self):
        """Create SessionLocal class"""
        if not self.engine:
            self.create_engine()

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        return self.SessionLocal

    def get_session(self) -> Session:
        """Get database session"""
        if not self.SessionLocal:
            self.create_session_local()
        return self.SessionLocal()

    def init_database(self):
        """Initialize database tables"""
        if not self.engine:
            self.create_engine()

        try:
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    async def test_connection(self) -> bool:
        """Test database connection (async)"""
        try:
            if not self.engine:
                self.create_engine()

            loop = asyncio.get_event_loop()
            with self.engine.connect() as conn:
                result = await loop.run_in_executor(None, lambda: conn.execute(text("SELECT 1")))
                return result.fetchone() is not None
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

# Global database configuration instance
db_config = DatabaseConfig()

# Convenience functions
def get_database_url() -> str:
    """Get the database URL"""
    return db_config.get_database_url()

def get_engine():
    """Get database engine"""
    if not db_config.engine:
        db_config.create_engine()
    return db_config.engine

def get_session() -> Session:
    """Get database session"""
    return db_config.get_session()

def init_db():
    """Initialize database"""
    db_config.init_database()

def test_db_connection() -> bool:
    """Test database connection"""
    return db_config.test_connection()

# Database dependency for FastAPI
def get_db():
    """Database dependency for FastAPI routes"""
    db = get_session()
    try:
        yield db
    finally:
        db.close()

# Migration utilities
class MigrationUtil:
    """Utilities for database migrations"""

    @staticmethod
    async def check_table_exists(table_name: str) -> bool:
        """Check if a table exists (async)"""
        try:
            engine = get_engine()
            loop = asyncio.get_event_loop()
            with engine.connect() as conn:
                result = await loop.run_in_executor(None, lambda: conn.execute(text(
                    f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
                )))
                return result.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False

    @staticmethod
    def get_table_info(table_name: str) -> Dict[str, Any]:
        """Get table information"""
        try:
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"PRAGMA table_info({table_name})"))
                columns = result.fetchall()
                return {
                    "table_name": table_name,
                    "columns": [dict(col._mapping) for col in columns]
                }
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            return {}
