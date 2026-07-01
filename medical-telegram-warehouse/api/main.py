# api/main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from .database import get_db
from .import schemas

app = FastAPI(
    title="Kara Solutions Medical Warehouse Analytics API",
    description="REST endpoints providing insights on Ethiopian pharmaceutical, cosmetic, and medical Telegram feeds.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "online", "docs_url": "/docs"}

# Endpoint 1 — Top Mentioned Terms/Products
@app.get("/api/reports/top-products")
def get_top_products(limit: int = 10, db: Session = Depends(get_db)):
    # Simple keyword parsing from message text for top product extraction
    query = text(r"""
        SELECT word, count(*) as mention_count
        FROM (
            SELECT regexp_split_to_table(lower(message_text), '\s+') as word 
            FROM analytics.fct_messages
            WHERE message_text IS NOT NULL
        ) words
        WHERE length(word) > 4 
          AND word NOT IN ('https', 'about', 'there', 'their', 'would', 'shall')
        GROUP BY word
        ORDER BY mention_count DESC
        LIMIT :limit;
    """)
    result = db.execute(query, {"limit": limit}).fetchall()
    return [{"product_keyword": row[0], "mentions": row[1]} for row in result]

# Endpoint 2 — Channel Activity Trends
@app.get("/api/channels/{channel_name}/activity", response_model=schemas.ChannelActivityResponse)
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    query = text(r"""
        SELECT channel_name, channel_type, total_posts, avg_views 
        FROM analytics.dim_channels 
        WHERE lower(channel_name) = lower(:channel_name);
    """)
    row = db.execute(query, {"channel_name": channel_name}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Channel profile '{channel_name}' not found.")
    return schemas.ChannelActivityResponse(
        channel_name=row[0],
        channel_type=row[1],
        total_posts=row[2],
        avg_views=row[3]
    )

# Endpoint 3 — Message Text Keyword Search
@app.get("/api/search/messages", response_model=List[schemas.MessageSearchResponse])
def search_messages(query: str, limit: int = 20, db: Session = Depends(get_db)):
    sql_query = text(r"""
        SELECT message_id, channel_key, message_text, views_count, forwards_count 
        FROM analytics.fct_messages 
        WHERE message_text ILIKE :search_str
        LIMIT :limit;
    """)
    results = db.execute(sql_query, {"search_str": f"%{query}%", "limit": limit}).fetchall()
    return [
        schemas.MessageSearchResponse(
            message_id=row[0],
            channel_key=row[1],
            message_text=row[2],
            views_count=row[3],
            forwards_count=row[4]
        ) for row in results
    ]

# Endpoint 4 — Visual Content Detection Metrics (YOLO joins)
@app.get("/api/reports/visual-content", response_model=List[schemas.VisualStatResponse])
def get_visual_stats(db: Session = Depends(get_db)):
    query = text(r"""
        SELECT c.channel_name, i.image_category, count(*) as total_images, round(avg(i.confidence_score)::numeric, 4) as avg_conf
        FROM analytics.fct_image_detections i
        JOIN analytics.dim_channels c ON i.channel_key = c.channel_key
        WHERE i.image_category IS NOT NULL
        GROUP BY c.channel_name, i.image_category
        ORDER BY total_images DESC;
    """)
    results = db.execute(query).fetchall()
    return [
        schemas.VisualStatResponse(
            channel_name=row[0],
            image_category=row[1],
            total_images=row[2],
            avg_confidence=float(row[3])
        ) for row in results
    ]