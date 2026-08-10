{{ config (
materialized = 'table'
)
}}

with silver as(
    SELECT * FROM {{ref('transformation')}} 
)

SELECT 
property_id,
property_status,
md5(cast(extracted_at as varchar)) AS fk_date,
md5(CONCAT(city_name,'-',neighborhood_final)) AS geo_fk,
md5(CONCAT(
    COALESCE(cast(socioeconomic_stratum as varchar),'0'), '-',
    COALESCE(cast(rooms as varchar),'0'), '-',
    COALESCE(cast(bathrooms as varchar),'0'), '-',
    COALESCE(cast(garages as varchar),'0'), '-',
    COALESCE(cast(total_area as varchar),'0'), '-',
    property_type
)) AS feature_fk,
reting_price,
administration_value,
days_on_market,
days_off_market,
longitude,
latitude,
CONCAT('https://www.metrocuadrado.com','',property_link) as link
FROM (
SELECT 
rent_value as reting_price,
COALESCE(administration_value, 0) as administration_value,
property_id,
extracted_at,
neighborhood_final,
city_name,
total_area,
rooms,garages,bathrooms,property_type,socioeconomic_stratum,
property_status, longitude,latitude,days_on_market,days_off_market,property_type, property_link
FROM silver) AS t