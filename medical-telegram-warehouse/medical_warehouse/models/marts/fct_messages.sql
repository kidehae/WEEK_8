{{ config(materialized='table') }}

with staging_messages as (
    select * from {{ ref('stg_telegram_messages') }}
),

final as (
    select
        m.surrogate_key as message_id,
        md5(m.channel_name) as channel_key,
        to_char(m.message_timestamp, 'YYYYMMDD')::int as date_key,
        m.message_text,
        length(m.message_text) as message_length,
        m.views_count,
        m.forwards_count,
        m.has_media as has_image_flag
    from staging_messages m
)

select * from final