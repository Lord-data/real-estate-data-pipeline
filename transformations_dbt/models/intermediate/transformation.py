import pandas as pd
from rapidfuzz import fuzz, process


def cleaning (row, df_seed, threshold = 65):
    
    messy_hood = row['common_neighborhood_name']
    city_name = row['city_name']
    
    if pd.isna(messy_hood) or city_name == '':
        return messy_hood
    
    
    city_seed = df_seed[df_seed['city_name'] == city_name]['neighborhood_official_name'].tolist()
    
    if not city_seed:
        return messy_hood
    result = process.extractOne(messy_hood, city_seed, scorer = fuzz.token_sort_ratio)
    
    if result:
       candidate_hood,score, _ = result
       
       if score >= threshold:
           return candidate_hood
       else:
           return messy_hood
       
    return messy_hood    
      
def model(dbt,session):
    # duckdb config
    dbt.config(
        materialized = "table",
        schema = 'intermediate',
        submission_method = "local"
    )
    
    # getting df from duckdb
    df_silver = dbt.ref("silver").df()
    df_seed = dbt.ref("final_seed").df()
    df_silver['neighborhood_final'] = df_silver.apply(cleaning,axis = 1, args = (df_seed, 65))
    
    return df_silver     