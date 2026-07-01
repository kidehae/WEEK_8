# pipeline.py
import subprocess
import os
from dagster import asset, Definitions, AssetExecutionContext

@asset(compute_kind="python")
def scrape_telegram_data(context: AssetExecutionContext):
    """Task 1: Ingests raw data structures from target public medical Telegram channels."""
    context.log.info("Kicking off Telethon scraper pipeline asset loop...")
    result = subprocess.run(["python", "src/scraper.py"], capture_output=True, text=True, check=True)
    context.log.info(result.stdout)

@asset(deps=[scrape_telegram_data], compute_kind="python")
def load_raw_to_postgres(context: AssetExecutionContext):
    """Task 2: Ingests raw structured partition JSON maps directly into PostgreSQL schemas."""
    context.log.info("Streaming raw data lake payloads into postgres relational maps...")
    result = subprocess.run(["python", "src/load_to_postgres.py"], capture_output=True, text=True, check=True)
    context.log.info(result.stdout)

@asset(deps=[load_raw_to_postgres], compute_kind="python")
def run_yolo_enrichment(context: AssetExecutionContext):
    """Task 3: Executes YOLOv8 object vision models against downloaded channel image logs."""
    context.log.info("Executing YOLOv8 nano model object detection profiling rules...")
    result = subprocess.run(["python", "src/yolo_detect.py"], capture_output=True, text=True, check=True)
    context.log.info(result.stdout)

@asset(deps=[run_yolo_enrichment], compute_kind="dbt")
def run_dbt_transformations(context: AssetExecutionContext):
    """Tasks 2 & 3: Compiles seed listings and runs the complete dbt dimensional star schema models."""
    context.log.info("Synchronizing data mart models inside dbt directory workspace...")
    
    # Change working path context to dbt project folder level explicitly
    dbt_path = os.path.abspath("medical_warehouse")
    seed_path = os.path.abspath("data/yolo_detections.csv")
    target_seed_dir = os.path.join(dbt_path, "seeds")
    
    # Mirror freshly extracted YOLO metrics over into seeds for staging ingestion
    os.makedirs(target_seed_dir, exist_ok=True)
    subprocess.run(["cp", seed_path, os.path.join(target_seed_dir, "yolo_detections.csv")], check=True)

    # Compile and re-deploy schemas sequentially
    subprocess.run(["dbt", "seed", "--profiles-dir", "."], cwd=dbt_path, check=True)
    result = subprocess.run(["dbt", "run", "--profiles-dir", "."], cwd=dbt_path, capture_output=True, text=True, check=True)
    context.log.info(result.stdout)

# Bundle our functional assets into a single cohesive global environment definition
defs = Definitions(
    assets=[scrape_telegram_data, load_raw_to_postgres, run_yolo_enrichment, run_dbt_transformations]
)