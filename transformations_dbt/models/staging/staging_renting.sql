{{ config(
    materialized='view'
) }}

with source_data as (
    -- dbt maneja el read_parquet y el union_by_name a través de la configuración del source en el .yml
    select * from {{ source('raw_renting', 'colombia_renting') }}
),

renamed_and_cleaned as (
    select
        -- Llaves primarias / Identificadores
        midinmueble as property_id,
        midempresa as company_id,
        
        -- Información del inmueble
        title as property_title,
        link as property_link,
        mbarrio as neighborhood,
        mnombrecomunbarrio as common_neighborhood_name,
        "MTIPOINMUEBLE.NOMBRE" as property_type, 
        "MCIUDAD.NOMBRE" as city_name,           
        "MZONA.NOMBRE" as zone_name,            
         
        -- Características físicas (Limpieza de Regex + TRY_CAST seguro)
        cast(marea as float) as total_area,
        try_cast(regexp_replace(cast(mnrocuartos as varchar), '[^0-9]+', '', 'g') as integer) as rooms_count,
        try_cast(regexp_replace(cast(mnrobanos as varchar), '[^0-9]+', '', 'g') as integer) as bathrooms_count,
        try_cast(regexp_replace(cast(mnrogarajes as varchar), '[^0-9]+', '', 'g') as integer) as garages_count,
        try_cast(estrato as integer) as socioeconomic_stratum,
        
        -- Costos
        cast(mvalorarriendo as float) as rent_value,
        cast("DATA.MVALORADMINISTRACION" as float) as administration_value, 
        
        -- Coordenadas Geográficas
        cast("LOCALIZACION.LON" as float) as longitude, 
        cast("LOCALIZACION.LAT" as float) as latitude,  
        
        -- Metadata de control de carga
        uploaded_date as extracted_at,
        load_type
        
    from source_data
)

SELECT * FROM 
renamed_and_cleaned