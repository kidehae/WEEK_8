
```markdown
# Medical Telegram Warehouse (Data Engineering Pipeline)

An end-to-end data engineering pipeline that scrapes medical, pharmaceutical, and cosmetics data from public Telegram channels, ingests the unstructured logs into a raw data lake, streams them into a PostgreSQL warehouse, and structures them into an analytical schema using dbt Core.

---

## Project Architecture

1. **Data Ingestion (Task 1):** A Python script using the Telethon library connects to the Telegram API to fetch raw text data and binary media assets from regional channels (`@CheMed`, `@Lobeliacosmetics`, and `@tikvahpharma`). Data is securely persisted into date-partitioned raw files (`data/raw/`).
2. **Database Loading (Task 2 - Part A):** A custom Python script structures the JSON inputs and executes atomic bulk inserts into a staging schema within a PostgreSQL database instances.
3. **Data Modeling (Task 2 - Part B):** dbt (Data Build Tool) builds compile-ready SQL workflows to transform raw staging tables into query-optimized Views and production Star-Schema Data Marts.

---

## Directory Structure

```text
medical-telegram-warehouse/
├── data/
│   └── raw/
│       ├── telegram_messages/   # Date-partitioned raw JSON files (YYYY-MM-DD)
│       └── images/              # Downloaded binary image assets grouped by channel
├── src/
│   ├── scraper.py               # Telethon scraper script
│   ├── load_to_postgres.py      # Bulk DB loader script
│   └── utils.py                 # Core loggers and environment configuration utilities
├── medical_warehouse/           # Complete dbt Core project workspace
│   ├── dbt_project.yml          # Core execution and layer configurations
│   ├── profiles.yml             # Local database target credentials mapping
│   └── models/
│       ├── staging/             # Cleaning, casting, and raw testing layer
│       │   ├── schema.yml       # Source schemas and constraint tests
│       │   └── stg_telegram_messages.sql
│       └── marts/               # Final production fact and dimension models
├── .env                         # Local environment configuration secrets
└── requirements.txt             # Python dependency manifest

```

---

## Getting Started

### 1. Prerequisites & Environment Setup

Ensure you have Python 3.10+ and a local PostgreSQL instance installed.

Clone this repository, then create and activate a virtual environment:

```bash
# Create environment
python -m venv .venv

# Activate environment (Git Bash / Linux)
source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

```

### 2. Configuration (`.env`)

Create a `.env` file in the root directory of your project to store local API configuration variables and database targets. **Do not omit the `TG_` prefix:**

```ini
TG_API_ID=31147898
TG_API_HASH=dd742b907083f3f482e2a83a5b5f8753
DB_USER=postgres
DB_PASSWORD=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=week_8

```

---

## Execution Pipeline

### Step 1: Run the Telegram Scraper

Execute the data lake collection script. On the initial execution, the terminal will safely ask for your international phone number (e.g., `+2519...`) and verification code to authenticate your session token.

```bash
python src/scraper.py

```

*This downloads the latest message records and writes files directly into your `data/raw/` path.*

### Step 2: Ingest Raw Data into PostgreSQL

Ensure your database instance (configured as `week_8`) exists inside PostgreSQL, then execute the bulk ingest loader:

```bash
python src/load_to_postgres.py

```

*This creates the `raw` schema inside your database and transfers the JSON blocks directly into the `raw.telegram_messages` database table.*

### Step 3: Run Data Modeling Transformations (dbt)

Navigate into your dedicated dbt analytics workspace subfolder:

```bash
cd medical_warehouse

```

Test your database connection profile handshake to make sure it can see your PostgreSQL warehouse configuration:

```bash
dbt debug --profiles-dir .

```

If the checks pass cleanly, execute your data cleaning transformation logic to build your analytics-ready Views:

```bash
dbt run --profiles-dir .

```

To run structural data validation tests ensuring zero missing values or duplicate key constraints exist across keys:

```bash
dbt test --profiles-dir .

```

---

## Data Transformation Rules (Staging Layer)

The dbt transformation view handles a variety of data anomalies present within the primitive scraping logs:

* **Casting & Timestamps:** Explicitly converts varying incoming character dates into formal database `timestamp` fields.
* **Missing Text Imputation:** Catches missing strings or empty messages using `coalesce` fallbacks.
* **Metric Coercion:** Fallbacks all empty numeric rows for metric calculations (such as views count or total forward frequencies) cleanly to `0` to streamline aggregation functions.

```
