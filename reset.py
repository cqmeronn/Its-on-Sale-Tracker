"""Drop and recreate all tables from ORM definitions."""

from sqlalchemy import text
from pipeline.common.db import engine
from pipeline.common.models import Base

with engine.begin() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
Base.metadata.create_all(bind=engine)
print("Database reset and schema recreated.")
