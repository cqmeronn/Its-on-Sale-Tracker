# It’s On Sale Tracker  
**A pipeline to monitor product price data (currently in progress).**

> **Note:** Still in active development. The ingestion, transformation, and CI/CD foundation are complete — Streamlit UI and data quality alerting will be added next.

---

## Project Overview

**It’s On Sale Tracker** is a data engineering project built to demonstrate a full end-to-end data workflow — from ingestion to transformation and visualization — using modern, production-like tooling.

It scrapes product data from the web (currently using `books.toscrape.com` as a demo source), stores it in a PostgreSQL database (via [Neon](https://neon.tech)), transforms it using **dbt**, and runs automatically in **GitHub Actions** on a schedule.

---

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|----------|
| **Ingestion** | `requests`, `BeautifulSoup4`, `lxml`, `loguru` | Scrape product data from websites |
| **Database** | `PostgreSQL` (Neon) + `SQLAlchemy` | Store product and price history data |
| **Transformation** | `dbt-core`, `dbt-postgres` | Clean and model data for analysis |
| **Validation** | `dbt tests` (and soon `Great Expectations`) | Ensure data quality and integrity |
| **Orchestration / CI** | `GitHub Actions` | Run ingestion + dbt on a 5-minute schedule |
| **Visualization (WIP)** | `Streamlit` | Simple dashboard for price history |
| **Environment** | `.env` + `python-dotenv` | Manage secrets and configuration |

---

## Project Structure

```
its-on-sale-tracker/
│
├── .github/workflows/pipeline.yml      # CI/CD pipeline
├── pipeline/
│   ├── common/                         # Shared config, DB engine, ORM models
│   ├── ingest/                         # Data fetching and parsing
│   │   ├── fetch_and_parse.py          # Fetch product HTML + parse details
│   │   └── parsers/books_to_scrape.py  # Parser for demo website
│   ├── load/                           # Insert data into Postgres
│   ├── transform/its_on_sale/          # dbt project
│   │   ├── models/staging/             # stg_product, stg_price_history
│   │   └── models/marts/               # fact_price_history, latest_price_per_product
│   └── dq/                             # (to be added) Great Expectations
│
├── streamlit_app/                      # Streamlit app (WIP)
│   └── app.py
│
├── .env.example                        # Example env file for local setup
├── requirements.txt                    # Dependencies
└── README.md
```

---

## Current Features

### 1. Ingestion
- Scrapes product data (name, price, currency, availability) from **Books to Scrape**.
- Modular parser design (can extend easily to Amazon, Argos, etc.).
- Logged with `loguru` for visibility.

### 2. Database
- SQLAlchemy ORM with models for `product` and `price_history`.
- Automatic table creation + Neon PostgreSQL connection.
- Local `.env` support and GitHub Actions secret handling.

### 3. Transformations (dbt)
- dbt project: `its_on_sale`
- Models:
  - `stg_product`
  - `stg_price_history`
  - `fact_price_history`
  - `latest_price_per_product`
- Relationship + uniqueness tests integrated and passing.
- dbt runs automatically in CI.

### 4. CI/CD (GitHub Actions)
- Full pipeline triggered:
  1. Install dependencies
  2. Parse Neon DB URL → env vars
  3. Run ingestion (`python -m pipeline.ingest.fetch_and_parse`)
  4. Run `dbt debug`, `dbt run`, and `dbt test`
- Scheduled every 5 minutes + manual dispatch.
- Uses Neon DB secrets securely via `secrets.NEON_DATABASE_URL`.

### 5. Streamlit (In Progress)
- Basic app implemented (`streamlit_app/app.py`)
- Reads from Neon DB, displays products + price history.
- Deployment to Streamlit Cloud planned for next phase.

---

## Run Locally

### Prerequisites
- Python 3.11
- Git
- Neon PostgreSQL account (or local Postgres)
- (Optional) Virtualenv: `python -m venv .venv`

### Setup
```bash
git clone https://github.com/cqmeronn/Its-on-Sale-Tracker.git
cd Its-on-Sale-Tracker
pip install -r requirements.txt
```

Create your `.env` file:
```
DATABASE_URL=postgresql+psycopg://user:password@host/dbname
```

Initialize the database:
```bash
python -m pipeline.load.init_db
python -m pipeline.load.test_connection
```

Run the ingestion:
```bash
python -m pipeline.ingest.fetch_and_parse
```

Run dbt locally:
```bash
cd pipeline/transform/its_on_sale
dbt debug
dbt run
dbt test
```

Run Streamlit:
```bash
streamlit run streamlit_app/app.py
```

## CI/CD Status

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/cqmeronn/Its-on-Sale-Tracker/pipeline.yml?branch=main)
![GitHub last commit](https://img.shields.io/github/last-commit/cqmeronn/Its-on-Sale-Tracker)
![GitHub repo size](https://img.shields.io/github/repo-size/cqmeronn/Its-on-Sale-Tracker)