{{ config(
materialized = 'table'
)
}}

with silver as (
    SELECT * FROM {{ref('transformation')}}
)

SELECT DISTINCT 
md5(cast(extracted_at as varchar)) AS date_key,
extracted_at,
extract(year from extracted_at) as year,
extract(month from extracted_at) as month
from silver