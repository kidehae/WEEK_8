{{ config(materialized='table') }}

with staging_data as (
    select * from {{ ref('stg_telegram_messages') }}
),

channel_metrics as (
    select
        channel_name,
        -- Generate a predictable unique key for each channel
        md5(channel_name) as channel_key,
        case 
            when channel_name = 'tikvahpharma' then 'Pharmaceutical'
            when channel_name = 'Lobeliacosmetics' then 'Cosmetics'
            else 'Medical'
        end as channel_type,
        min(message_timestamp) as first_post_date,
        max(message_timestamp) as last_post_date,
        count(distinct surrogate_key) as total_posts,
        round(avg(views_count), 2) as avg_views
    from staging_data
    group by channel_name
)

select * from channel_metrics