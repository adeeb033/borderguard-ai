import os
from pathlib import Path

import psycopg2


def _load_env_file():
    """Load a project-level .env into os.environ without extra dependencies."""
    env_locations = [
        Path(__file__).resolve().parent.parent / ".env",
        Path(__file__).resolve().parent / ".env",
        Path.cwd() / ".env",
    ]

    for env_path in env_locations:
        if not env_path.exists():
            continue

        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue

            key, value = stripped.split("=", 1)
            os.environ[key.strip()] = value.strip().strip('"').strip("'")


_load_env_file()


def get_db_connection():
    database_url = os.getenv("SUPABASE_DB_URL")
    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host=os.getenv("SUPABASE_DB_HOST", "localhost"),
        port=int(os.getenv("SUPABASE_DB_PORT", "5432")),
        database=os.getenv("SUPABASE_DB_NAME", "postgres"),
        user=os.getenv("SUPABASE_DB_USER", "postgres"),
        password=os.getenv("SUPABASE_DB_PASSWORD", "postgres"),
        sslmode=os.getenv("SUPABASE_SSLMODE", "require"),
    )
