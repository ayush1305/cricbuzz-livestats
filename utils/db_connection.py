"""
Centralized Database Connection Handler for Cricbuzz LiveStats.
Supports SQLite (default), PostgreSQL, and MySQL.
Provides SQLite polyfills for STDDEV and window/analytical compatibility.
"""

import os
import math
import sqlite3
from typing import Optional, Tuple, Any, Dict
import pandas as pd
from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Singleton engine cache
_ENGINE: Optional[Engine] = None
_CURRENT_DB_URL: Optional[str] = None


class StdDevAggregate:
    """Python-based SQLite aggregate function for STDDEV / STDDEV_POP."""
    def __init__(self):
        self.values = []

    def step(self, value):
        if value is not None:
            try:
                self.values.append(float(value))
            except (ValueError, TypeError):
                pass

    def finalize(self):
        n = len(self.values)
        if n < 2:
            return 0.0
        mean = sum(self.values) / n
        variance = sum((x - mean) ** 2 for x in self.values) / (n - 1)
        return math.sqrt(variance)


def register_sqlite_functions(dbapi_connection, connection_record):
    """Register custom functions like STDDEV on raw SQLite connections."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        dbapi_connection.create_aggregate("stddev", 1, StdDevAggregate)
        dbapi_connection.create_aggregate("stddev_pop", 1, StdDevAggregate)


def get_default_db_path() -> str:
    """Returns absolute path to local SQLite database."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "database", "cricket_analytics.db")


def get_database_url() -> str:
    """
    Determines the Database URL based on Streamlit Secrets, environment variables, or defaults to SQLite.
    """
    # 0. Check Streamlit Secrets (for Streamlit Cloud deployments)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "DATABASE_URL" in st.secrets:
                return st.secrets["DATABASE_URL"]
            if "DB_TYPE" in st.secrets and st.secrets["DB_TYPE"] == "postgresql":
                h = st.secrets.get("DB_HOST", "localhost")
                p = st.secrets.get("DB_PORT", "5432")
                d = st.secrets.get("DB_NAME", "cricket_analytics")
                u = st.secrets.get("DB_USER", "postgres")
                pwd = st.secrets.get("DB_PASSWORD", "")
                return f"postgresql+psycopg2://{u}:{pwd}@{h}:{p}/{d}"
    except Exception:
        pass

    # 1. Direct DATABASE_URL check
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # 2. Check DB_TYPE
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    if db_type == "postgresql":
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        db = os.getenv("DB_NAME", "cricket_analytics")
        user = os.getenv("DB_USER", "postgres")
        pwd = os.getenv("DB_PASSWORD", "")
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"

    elif db_type == "mysql":
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        db = os.getenv("DB_NAME", "cricket_analytics")
        user = os.getenv("DB_USER", "root")
        pwd = os.getenv("DB_PASSWORD", "")
        return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"

    # Default to SQLite
    sqlite_path = os.getenv("SQLITE_DB_PATH") or get_default_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(sqlite_path)), exist_ok=True)
    return f"sqlite:///{sqlite_path}"


def get_engine(db_url: Optional[str] = None) -> Engine:
    """Returns a singleton or configured SQLAlchemy Engine."""
    global _ENGINE, _CURRENT_DB_URL
    target_url = db_url or get_database_url()

    if _ENGINE is None or _CURRENT_DB_URL != target_url:
        is_sqlite = target_url.startswith("sqlite")
        connect_args = {"check_same_thread": False} if is_sqlite else {}

        _ENGINE = create_engine(
            target_url,
            connect_args=connect_args,
            pool_pre_ping=True,
            echo=False
        )
        _CURRENT_DB_URL = target_url

        if is_sqlite:
            event.listen(_ENGINE, "connect", register_sqlite_functions)

        # Self-heal and guarantee career numbers are populated
        try:
            from utils.enrich_data import ensure_database_enriched
            ensure_database_enriched(_ENGINE)
        except Exception:
            pass

    return _ENGINE


def test_connection(db_url: str) -> Tuple[bool, str]:
    """Tests connection to a specified database URL."""
    try:
        engine = create_engine(db_url, pool_pre_ping=True)
        if db_url.startswith("sqlite"):
            event.listen(engine, "connect", register_sqlite_functions)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Connection successful! Database is accessible."
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def _sanitize_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not params:
        return params
    clean = {}
    for k, v in params.items():
        if hasattr(v, "item"):
            clean[k] = v.item()
        else:
            clean[k] = v
    return clean


def execute_query(sql_query: str, params: Optional[Dict[str, Any]] = None, db_url: Optional[str] = None) -> pd.DataFrame:
    """
    Executes a SELECT query and returns the results as a Pandas DataFrame.
    """
    engine = get_engine(db_url)
    clean_p = _sanitize_params(params)
    with engine.connect() as conn:
        df = pd.read_sql_query(text(sql_query), conn, params=clean_p)
    return df


def execute_statement(sql_stmt: str, params: Optional[Dict[str, Any]] = None, db_url: Optional[str] = None) -> int:
    """
    Executes an INSERT / UPDATE / DELETE statement and commits changes.
    Returns rows affected.
    """
    engine = get_engine(db_url)
    clean_p = _sanitize_params(params)
    with engine.begin() as conn:
        result = conn.execute(text(sql_stmt), clean_p or {})
        return result.rowcount


def init_database(db_url: Optional[str] = None) -> None:
    """Creates schema tables if they do not exist."""
    engine = get_engine(db_url)
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "schema.sql")
    
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        # Split and execute statements
        statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))
