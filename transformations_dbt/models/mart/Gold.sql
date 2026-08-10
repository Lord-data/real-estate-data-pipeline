{{config(
materialized = 'table'
)
}}

with mart as (
    select * from {{ref('transformation')}}
)

SELECT neighborhood_final, city_name, count(neighborhood_final) as neighborhood_per_city FROM mart
GROUP BY neighborhood_final, city_name
HAVING neighborhood_per_city > 1 
ORDER BY neighborhood_per_city DESC