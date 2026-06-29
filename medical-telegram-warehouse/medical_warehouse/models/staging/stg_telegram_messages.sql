{{ config(materialized='view') }}

with raw_source as (
    select * from {{ source('raw', 'telegram_messages') }}
),

cleaned as (
    select
        id as surrogate_key,
        message_id,
        channel_name,
        message_date::timestamp as message_timestamp,
        coalesce(message_text, '') as message_text,
        has_media,
        image_path,
        coalesce(views, 0) as views_count,
        coalesce(forwards, 0) as forwards_count,
        ingested_at
    from raw_source
)

select * from cleaned