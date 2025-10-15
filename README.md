# It’s On Sale Tracker  
**A pipeline to monitor product price data (currently in progress).**

> **Note:** Still in active development. The ingestion, transformation, and CI/CD foundation are complete — Streamlit UI, data quality alerting, and Slack notifications are now integrated.

---

## Project Overview

**It’s On Sale Tracker** is a data engineering project built to demonstrate a full end-to-end data workflow — from ingestion to transformation, validation, and visualization — using modern, production-like tooling.

It scrapes product data from the web (currently using `books.toscrape.com` as a demo source), stores it in a PostgreSQL database (via [Neon](https://neon.tech)), transforms it using **dbt**, validates data quality using **Great Expectations**, and runs automatically in **GitHub Actions** on a schedule. Slack alerts are sent with summaries and notifications.

---

## Tech Stack

| Layer | Tool | Purpose |
|-------|------|----------|
| **Ingestion** | `requests`, `BeautifulSoup4`, `lxml`, `loguru` | Scrape product data from websites |
| **Database** | `PostgreSQL` (Neon) + `SQLAlchemy` | Store product and price history data |
| **Transformation** | `dbt-core`, `dbt-postgres` | Clean and model data for analysis |
| **Validation** | `dbt tests`, `Great Expectations` | Ensure data quality and integrity |
| **Orchestration / CI** | `GitHub Actions` | Run ingestion + dbt + validation + alerts |
| **Notification** | `Slack Webhooks` | Post summaries and price alerts to Slack |
| **Visualization (WIP)** | `Streamlit` | Dashboard for price history and changes |
| **Environment** | `.env` + `python-dotenv` | Manage secrets and configuration |

---

## Project Structure

```
its-on-sale-tracker/
│
├── .github/workflows/
├── pipeline/
│   ├── common/                         # Shared config, DB engine, ORM models
│   ├── dq/
│   │   └── run_dq_checks.py            # Great Expectations entrypoint
│   ├── ingest/
│   │   ├── fetch_and_parse.py          # Fetch product HTML + parse details
│   │   └── parsers/
│   │       ├── books_to_scrape.py      # Demo parser: books.toscrape.com
│   │       └── webscraper_io.py        # Demo parser: webscraper.io
│   ├── load/
│   │   ├── alert_price_drops.py        # Detect price drops + Slack alerts
│   │   ├── init_db.py                  # Create schemas/tables
│   │   ├── report_summary.py           # Post run summary to Slack
│   │   ├── seed_products.py            # Seed initial product rows
│   │   └── upsert.py                   # Upsert product + price rows
│   └── transform/
│       └── its_on_sale/                # dbt project root
│           ├── models/
│           │   ├── marts/
│           │   │   ├── fact_price_history.sql
│           │   │   ├── latest_price_per_product.sql
│           │   │   ├── price_events.sql
│           │   │   └── marts.yml
│           │   └── staging/
│           │       ├── staging.yml
│           │       ├── stg_price_history.sql
│           │       └── stg_product.sql
│           ├── .user.yml
│           └── dbt_project.yml
├── streamlit_app/
│   └── app.py                          # (WIP) dashboard
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── reset.py                            # One-command reset & full run

```

---

## Current Features

### 1. Ingestion
- Scrapes product data (name, price, currency, availability) from **Books to Scrape** and demo e-commerce pages.
- Modular parser design (extensible to Amazon, Argos, etc.).
- Uses `loguru` for clean logging and `hashlib` for deduplication.

### 2. Database
- SQLAlchemy ORM with models for `product` and `price_history`.
- Automatic table creation + Neon PostgreSQL connection.
- Supports both local and remote environments via `.env`.

### 3. Transformations (dbt)
- dbt project: `its_on_sale`
- Models:
  - `stg_product`
  - `stg_price_history`
  - `fact_price_history`
  - `price_events`
  - `latest_price_per_product`
- Relationship, uniqueness, and custom tests integrated.
- dbt runs automatically in CI/CD.

### 4. Data Quality Checks
- Great Expectations integrated (`pipeline/dq/run_dq_checks.py`).
- Validates:
  - Non-null IDs, prices, and timestamps.
  - Positive numeric prices.
  - Currency validity (`GBP`, `USD`, etc.).
- Fails CI pipeline on validation errors.

### 5. CI/CD (GitHub Actions)
- Full pipeline executes on schedule and push:
  1. Install dependencies
  2. Set up Postgres connection from Neon secret
  3. Run ingestion (`python -m pipeline.ingest.fetch_and_parse`)
  4. Run dbt (`debug`, `run`, `test`)
  5. Run data quality checks (`Great Expectations`)
  6. Send Slack summaries and alerts
- Securely manages secrets via GitHub repository settings.

### 6. Slack Integration
- Slack webhook connected to a workspace channel (e.g., `#projects-tracking`).
- Posts formatted summaries like:
  ```
  *Latest price summary:*
  • *books.toscrape.com* – A Light in the Attic: 51.77 GBP
  • *webscraper.io* – iPad Mini Retina: 537.99 USD
  ```
- Supports bold text, bullet points, and hyperlink formatting.

### 7. Streamlit (In Progress)
- Displays live data from Neon DB.
- Product filters by site or search term.
- Price history visualization planned.

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
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

Initialize the database:
```bash
python -m pipeline.load.init_db
python -m pipeline.load.test_connection
```

Run ingestion and checks:
```bash
python -m pipeline.ingest.fetch_and_parse
python -m pipeline.dq.run_dq_checks
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

**Optional**: Reset:
```bash
python reset.py     # reset and run everything end-to-end
```



---

## CI/CD Status

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/cqmeronn/Its-on-Sale-Tracker/pipeline.yml?branch=main)
![GitHub last commit](https://img.shields.io/github/last-commit/cqmeronn/Its-on-Sale-Tracker)
![GitHub repo size](https://img.shields.io/github/repo-size/cqmeronn/Its-on-Sale-Tracker)
