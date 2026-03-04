#!/usr/bin/env python3
"""
Initialize PostgreSQL database with schema and seed data.

This script sets up the SteelWorks database by:
1. Creating all tables from db/schema.sql
2. Loading sample data from db/seed.sql

Usage:
    poetry run python init_db.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (takes precedence)
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD: Alternative config
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
    sys.exit(1)


def get_database_url() -> str:
    """
    Construct database URL from environment variables.

    Priority:
    1. DATABASE_URL environment variable
    2. Individual DB_* variables
    3. Default to localhost

    Returns:
        str: PostgreSQL connection string
    """
    # Check for explicit DATABASE_URL first
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")

    # Build from individual components
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "steelworks_db")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")

    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def run_sql_file(conn, filepath: Path) -> None:
    """
    Execute SQL from a file.

    Args:
        conn: psycopg2 connection object
        filepath: Path to SQL file

    Raises:
        FileNotFoundError: If SQL file doesn't exist
        psycopg2.Error: If SQL execution fails
    """
    if not filepath.exists():
        raise FileNotFoundError(f"SQL file not found: {filepath}")

    with open(filepath, "r") as f:
        sql = f.read()

    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    print(f"✓ Executed {filepath.name}")


def main() -> None:
    """Main database initialization routine."""
    try:
        database_url = get_database_url()
        print("🔌 Connecting to PostgreSQL...")
        print(f"   Connection string: {database_url.split('@')[0]}@{database_url.split('@')[1] if '@' in database_url else 'unknown'}")

        conn = psycopg2.connect(database_url)

        # Load schema
        schema_file = Path(__file__).parent / "db" / "schema.sql"
        print(f"📋 Loading schema from {schema_file.name}...")
        run_sql_file(conn, schema_file)

        # Load seed data
        seed_file = Path(__file__).parent / "db" / "seed.sql"
        print(f"🌱 Loading seed data from {seed_file.name}...")
        run_sql_file(conn, seed_file)

        conn.close()
        print("\n✅ Database initialization complete!")
        print("   Run Streamlit app with: streamlit run src/steelworks/app.py")

    except FileNotFoundError as e:
        print(f"❌ File error: {e}")
        sys.exit(1)
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed:")
        print(f"   {e}")
        print("\n   Check your DATABASE_URL or DB_* environment variables")
        print("   See .env.example for configuration options")
        sys.exit(1)
    except psycopg2.ProgrammingError as e:
        print(f"❌ SQL execution error:")
        print(f"   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
