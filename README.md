Markdown
# Shipping a Data Product: From Raw Telegram Data to an Analytical API

An end-to-end medical data platform consultancy project for **Kara Solutions** (Ethiopia). This platform automates the extraction, loading, computer vision enrichment, modeling, transformation, and API exposure of pharmaceutical, cosmetic, and medical data scraped from public Ethiopian Telegram channels.

---

## 🏗️ System Architecture & Pipeline Flow

The platform implements a modern, production-grade **ELT (Extract, Load, Transform)** framework orchestrated entirely as a unified asset dependency graph.

1. **Extract & Load (Data Lake)**: Scrapes text and media binary payloads from target Telegram channels via Telethon, saving partitioned daily raw JSON documents.
2. **Relational Ingestion (Raw DWH Layer)**: Accumulates raw lake metrics into an isolated PostgreSQL landing zone schema (`raw.telegram_messages`).
3. **Computer Vision Enrichment (YOLOv8)**: Runs object-inferencing models across downloaded image feeds, classifying posts into target marketing categories (e.g., promotional vs. product display).
4. **Data Modeling & Analytics (dbt Marts)**: Builds a modular, fully validated Dimensional Star Schema (Fact and Dimension tables) optimized for fast business intelligence queries.
5. **Consumption Layer (FastAPI)**: Exposes analytical warehouse tables through validated, interactive REST endpoints.

---

## 📁 Project Structure

```text
medical-telegram-warehouse/
├── api/                           # Task 4: FastAPI Consumption Layer
│   ├── database.py                # SQLAlchemy DB session engine
│   ├── main.py                    # Analytical API endpoints & SQL queries
│   └── schemas.py                 # Pydantic request/response schemas
├── data/                          # Distributed Data Lake Storage
│   ├── raw/
│   │   ├── images/                # Downloaded media categorized by channel
│   │   └── telegram_messages/     # YYYY-MM-DD partitioned raw JSON feeds
│   └── yolo_detections.csv        # Computer vision intermediate enrichment layer
├── medical_warehouse/             # Task 2 & 3: dbt Dimensional Warehouse
│   ├── dbt_project.yml            # dbt Project configurations
│   ├── profiles.yml               # Warehouse connection targets
│   ├── models/
│   │   ├── staging/               # Raw cleaning, renaming, and type casting
│   │   └── marts/                 # Dim & Fact tables (Star Schema layer)
│   └── seeds/                     # YOLO vision seed target folder
├── src/                           # Core Data Engineering Pipelines
│   ├── scraper.py                 # Telethon async scraper engine
│   ├── load_to_postgres.py        # High-performance bulk relational loader
│   ├── yolo_detect.py             # YOLOv8 vision classification processor
│   └── utils.py                   # Global system logging utility
├── pipeline.py                    # Task 5: Dagster Orchestration Graph
├── docker-compose.yml             # Containerized services orchestration
├── Requirements.txt               # Main Python environment dependencies
└── README.md                      # Platform documentation
🛠️ Tech Stack & Core Tools
Orchestration: Dagster (Asset-Based Lineage)

Transformation & Testing: dbt (Data Build Tool) with dbt-postgres

Data Warehouse: PostgreSQL

Computer Vision: Ultralytics YOLOv8 (Nano Network)

API Development: FastAPI + Uvicorn + SQLAlchemy + Pydantic

Scraping Interface: Telethon (Telegram MTProto API Client)

🚀 Setup and Installation
1. Environment Configuration
Clone the repository and set up a Python virtual environment:

Bash
git clone <your-repository-url>
cd medical-telegram-warehouse
python -m venv .venv
source .venv/Scripts/activate  # On Windows: .venv\Scripts\Activate
pip install -r requirements.txt
2. Secrets & Environment Variables
Create a .env file in the root directory to store database credentials and Telegram API access keys securely (do not commit this file):

Code snippet
TG_API_ID=your_telegram_api_id
TG_API_HASH=your_telegram_api_hash
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgresql
DB_NAME=week_8
🔄 Running the Core Pipeline Component Steps
Step 1: Scrape Telegram Targets
Fetches target public handle feeds (@CheMed_News, @LobeliaCosmetics, @tikvahpharma) and partitions records:

Bash
python src/scraper.py
Step 2: Load to PostgreSQL Raw Schema
Streams local data lake JSON dumps straight into the relational warehouse:

Bash
python src/load_to_postgres.py
Step 3: Run YOLOv8 Object Classification
Processes downloaded image directories and formats categories into an intermediate enrichment output:

Bash
python src/yolo_detect.py
Step 4: Run dbt Transformations
Change directory into medical_warehouse/, initialize configurations, build seeds, and compile the entire dimensional star schema layer:

Bash
cd medical_warehouse
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
🎛️ Unified Orchestration & Consumption Apps
🏭 Automated Data Pipeline (Dagster UI)
To launch the centralized asset orchestration engine and view the end-to-end data lineage graph:

Bash
dagster dev -f pipeline.py
Open your browser and navigate to http://localhost:3000 to inspect execution logs or trigger a unified materialization run.

🌐 Serving Analytical Consumption Insights (FastAPI)
To bring up the REST API layer providing insights on top products, channel activity metrics, and computer vision counts:

Bash
python -m uvicorn api.main:app --reload
Navigate to http://127.0.0.1:8000/docs to access the fully interactive OpenAPI Swagger dashboard.

📊 Data Modeling: Warehouse Star Schema Design
The data mart transforms structured messages and model classifications into an optimized analytical layout:

dim_channels: Aggregates macro stats, post volumes, and assigns operational business channel sectors.

dim_dates: Comprehensive time dimension supporting day, week, month, quarter, and weekend analytics filtering.

fct_messages: Centralized operational fact tracking individual message details, views, forward volumes, and message lengths.

fct_image_detections: Links the computer vision output to the core message metrics to identify visual engagement trends.

📝 Authors & Contributors
Meaza Mulatu — Lead Data Engineer (Kara Solutions Consulting Partner)

Developed for 10 Academy: Week 8 Milestone Challenge (July 2026).
