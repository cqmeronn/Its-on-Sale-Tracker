"""Reset database schemas, rebuild tables, seed, ingest, run dbt and DQ."""
import os, re, subprocess, sys
from pathlib import Path
from sqlalchemy import text
from urllib.parse import urlparse
from sqlalchemy.orm import Session

from pipeline.common.db import engine, SessionLocal
from pipeline.common.models import Base
from pipeline.load.seed_products import main as seed_products
from pipeline.ingest.fetch_and_parse import main as run_ingestion
from pipeline.dq.run_dq_checks import main as run_dq
from pipeline.load.alert_price_drops import main as alert_drops
from pipeline.load.report_summary import main as report_summary

def find_repo_root(start: Path) -> Path:
    """Walk up until we find .git; fallback to current dir."""
    p = start.resolve()
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    return start.resolve()


ROOT = find_repo_root(Path(__file__).resolve().parent)
DBT_DIR = ROOT / "pipeline" / "transform" / "its_on_sale"
PROFILES_DIR = ROOT / "pipeline" / "transform"


def drop_and_recreate_schemas():
    """Drop and recreate public, staging, marts schemas."""
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS marts CASCADE;"))
        conn.execute(text("DROP SCHEMA IF EXISTS staging CASCADE;"))
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.execute(text("CREATE SCHEMA staging;"))
        conn.execute(text("CREATE SCHEMA marts;"))
    print("Schemas recreated: public, staging, marts.")

def create_orm_tables():
    """Create ORM tables in public schema."""
    Base.metadata.create_all(bind=engine)
    print("ORM tables created in public.")

def parse_database_url_to_pg_env():
    """Return PG env vars from DATABASE_URL for dbt."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set.")
    # allow both postgresql:// and postgresql+psycopg://
    m = re.match(r"^postgresql(?:\+\w+)?:\/\/([^:]+):([^@]+)@([^\/]+)\/([^?]+)", db_url)
    if not m:
        raise RuntimeError(f"Could not parse DATABASE_URL: {db_url}")
    user, pwd, host, db = m.groups()
    return {
        "PGHOST": host,
        "PGUSER": user,
        "PGPASSWORD": pwd,
        "PGDATABASE": db,
        "PGPORT": os.getenv("PGPORT", "5432"),
        "DBT_PROFILES_DIR": PROFILES_DIR,
    }

def run_dbt():
    """Run dbt debug, run, and test."""
    env = os.environ.copy()
    env.update(parse_database_url_to_pg_env())
    env["DBT_PROFILES_DIR"] = str(PROFILES_DIR)
    cmds = [["dbt", "debug"], ["dbt", "run"], ["dbt", "test"]]
    for cmd in cmds:
        print(f"Running: {' '.join(cmd)} (cwd={DBT_DIR})")
        subprocess.run(cmd, cwd=str(DBT_DIR), check=True, env=env)



def reset_and_bootstrap():
    """Execute full reset and bootstrap pipeline."""
    drop_and_recreate_schemas()
    create_orm_tables()

    seed_products()

    with SessionLocal() as s:
        count = s.execute(text("select count(*) from public.product")).scalar_one()
        print(f"Seeded products: {count}")

    run_ingestion()

    run_dbt()

    run_dq()

    alert_drops()
    report_summary()

if __name__ == "__main__":
    try:
        reset_and_bootstrap()
        print("Reset and bootstrap complete.")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}: {e.cmd}")
        sys.exit(e.returncode)
    except Exception as e:
        print("Bootstrap failed:", e)
        sys.exit(1)
