"""Test database connectivity to Neon/Postgres."""

from sqlalchemy import text
from pipeline.common.db import engine

def main():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar_one()
            print(f"Connected to database successfully.")
            print(f"Postgres version: {version}")
    except Exception as e:
        print("Database connection failed:")
        print(e)

if __name__ == "__main__":
    main()