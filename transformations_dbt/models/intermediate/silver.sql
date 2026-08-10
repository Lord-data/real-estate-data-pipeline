{{ config (
    materialized = 'table'
) }}

with staging_data as (
    -- Asegúrate de que use EXACTAMENTE el nombre del archivo de staging que pasó en verde:
    select * from {{ ref('staging_renting') }}
),

cleaning as ( SELECT
        property_id,
        company_id,
        property_title,
        property_link,
        neighborhood,
        upper(common_neighborhood_name) as common_neighborhood_name,
        property_type, 
        city_name,           
        CASE 
            WHEN zone_name = '' THEN NULL
            WHEN zone_name = '-' THEN NULL
            ELSE zone_name
        END AS zone_name,            
        total_area,
        rooms_count,
        bathrooms_count,
        garages_count,
        socioeconomic_stratum,
        rent_value,
        administration_value, 
        longitude, 
        latitude,  
        extracted_at,
        load_type
    FROM staging_data    
),

days_on as (
    SELECT *,
    datediff('day',MIN(extracted_at) OVER (PARTITION BY property_id),
            MAX(extracted_at) OVER (PARTITION BY property_id)
        ) AS days_on_market 
    FROM cleaning    
),

active as (SELECT *
       FROM (
       SELECT *,
       row_number() 
       OVER(PARTITION BY property_id ORDER BY extracted_at DESC) AS
       Property_date 
       FROM days_on) AS df
       WHERE Property_date = 1
),

reference_status AS (SELECT *, 
    CASE
        WHEN reference_days > 7 THEN 'INACTIVE' ELSE 'ACTIVE'
    END AS property_status     
FROM(SELECT *,        
    datediff('day',extracted_at,current_date) AS reference_days  
    FROM active) AS updated_table)

SELECT 
    property_id,
    company_id,
    property_title,
    property_link,
    neighborhood,
    common_neighborhood_name,
    property_type,
    city_name,
    zone_name,
    total_area,
    socioeconomic_stratum,
    rent_value,
    longitude,
    latitude,
    extracted_at,
    load_type,
    property_status,
    reference_days,
    days_on_market,

    CASE 
        WHEN property_status = 'INACTIVE' THEN reference_days
        ELSE 0
    END AS days_off_market,    
    
    CASE 
        WHEN lower(property_type) IN ('local comercial','bodega','oficina','consultorio','edificio de oficinas','casa lote','lote','edificio de apartamentos')
        THEN 0 
        ELSE rooms_count
    END AS rooms,

    CASE 
        WHEN lower(property_type) IN ('local comercial','bodega','oficina','consultorio','edificio de oficinas','casa lote','lote','edificio de apartamentos') AND bathrooms_count IS NULL
        THEN 0
        ELSE bathrooms_count
    END AS bathrooms,

    CASE 
        WHEN lower(property_type) IN ('local comercial','bodega','oficina','consultorio','edificio de oficinas','casa lote','lote','edificio de apartamentos') AND garages_count IS NULL
        THEN 0
        ELSE garages_count
    END AS garages,

    CASE 
        WHEN lower(property_type) IN ('local comercial','bodega','oficina','consultorio','edificio de oficinas','casa lote','lote','edificio de apartamentos') AND administration_value IS NULL
        THEN 0
        ELSE administration_value
    END AS administration_value
    
FROM reference_status