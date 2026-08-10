{{config(
    materialized = 'table'
)
}}

with silver as (
    SELECT * FROM {{ref('transformation')}}
)

SELECT DISTINCT
md5(CONCAT(city_name,'-',neighborhood_final)) AS geo_key,
city_name,
neighborhood_final
FROM silver
