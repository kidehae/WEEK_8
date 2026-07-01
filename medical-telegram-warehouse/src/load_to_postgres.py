# src/load_to_postgres.py
import os
import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from utils import get_logger, load_dotenv

logger = get_logger("DBLoader")
load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )

def load_data_lake_to_postgres():
    # Identify today's data lake partition path
    today_str = datetime.now().strftime("%Y-%m-%d")
    partition_dir = f"data/raw/telegram_messages/{today_str}"
    
    if not os.path.exists(partition_dir):
        logger.error(f"No raw data directory partition found for date: {today_str}")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create staging database schema layer
        cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
        
        # Build the exact raw table mapping schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw.telegram_messages (
                id SERIAL PRIMARY KEY,
                message_id INT,
                channel_name VARCHAR(100),
                message_date TIMESTAMPTZ,
                message_text TEXT,
                has_media BOOLEAN,
                image_path TEXT,
                views INT,
                forwards INT,
                ingested_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        logger.info("Database structural target 'raw.telegram_messages' validated successfully.")

        # Read JSON file elements out of data lake directories
        all_records = []
        for file_name in os.listdir(partition_dir):
            if file_name.endswith(".json"):
                file_path = os.path.join(partition_dir, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    for item in file_data:
                        all_records.append((
                            item["message_id"],
                            item["channel_name"],
                            item["message_date"],
                            item["message_text"],
                            item["has_media"],
                            item["image_path"],
                            item["views"],
                            item["forwards"]
                        ))

        if all_records:
            # Atomic bulk insertion processing engine 
            insert_query = """
                INSERT INTO raw.telegram_messages 
                (message_id, channel_name, message_date, message_text, has_media, image_path, views, forwards)
                VALUES %s;
            """
            execute_values(cursor, insert_query, all_records)
            conn.commit()
            logger.info(f"Successfully loaded {len(all_records)} raw records into raw.telegram_messages.")
        else:
            logger.warning("No records collected from JSON file partitions.")

    except Exception as e:
        conn.rollback()
        logger.critical(f"Database bulk transmission aborted: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    load_data_lake_to_postgres()