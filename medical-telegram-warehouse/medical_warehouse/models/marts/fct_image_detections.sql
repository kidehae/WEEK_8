{{ config(materialized='table') }}

with yolo_seed as (
    select * from {{ ref('yolo_detections') }}
),

messages_mart as (
    select * from {{ ref('fct_messages') }}
),

final as (
    select
        y.message_id,
        m.channel_key,
        m.date_key,
        y.detected_class,
        y.confidence_score,
        y.image_category
    from yolo_seed y
    left join messages_mart m on y.message_id = m.message_id
)

select * from final