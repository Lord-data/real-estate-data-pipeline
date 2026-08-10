{{config(
    materialized = 'table',
)
}}

with silver as (
    SELECT * FROM {{ref('transformation')}}
)

SELECT DISTINCT
md5(CONCAT(
    COALESCE(cast(socioeconomic_stratum as varchar),'0'), '-',
    COALESCE(cast(rooms as varchar),'0'), '-',
    COALESCE(cast(bathrooms as varchar),'0'), '-',
    COALESCE(cast(garages as varchar),'0'), '-',
    COALESCE(cast(total_area as varchar),'0'), '-',
    property_type
)) AS feature_key,
socioeconomic_stratum,rooms,bathrooms,garages,total_area,property_type
from silver