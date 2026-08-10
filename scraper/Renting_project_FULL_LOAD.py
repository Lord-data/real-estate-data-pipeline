import logging
import os
import random
import time
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

SCRIPT_PATH = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_PATH / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path = ENV_PATH)
    # Global Headers
    HEADER = {
    "x-api-key": os.getenv("API_KEY"),
    "User-Agent": os.getenv("USER_AGENT")
    }
    
else:
    logging.critical("⚠️ .env file not found! Unable to initialize headers.")
    raise ValueError("API credentials not found!")        

# Logger setup with multiple outputs (Console + File)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding = 'utf-8',
    handlers=[
        logging.FileHandler("Full_ingestion.log"),
        logging.StreamHandler()
    ]
)

def catolog_size(header):
    logging.info("🚀 Starting catalog sizes check...")

    catalog_size1 = {}
    cities = [
        "medellin", "bogota", "cali", "itagui", "la-estrella", "sabaneta", "caldas", "bello",
        "barranquilla", "cartagena-de-indias", "bucaramanga", "soacha", "cucuta", "pereira",
        "manizales", "ibague", "santa-marta"
    ]

    for city in cities:
        try:
            logging.info(f"Checking catalog size for city: {city}...")
            url = f"https://www.metrocuadrado.com/rest-search/search?size=50&from=0&realEstateBusinessList=arriendo&city={city}"
            response = requests.get(url, headers=header, timeout=10)

            if response.status_code == 200:
                data = response.json()
                total_entries = data.get("totalEntries", 0)
                catalog_size1[city] = total_entries
                logging.info(f"  -> {city}: {total_entries} records found.")
            else:
                logging.warning(f"  ❌ {city} returned an invalid status code: {response.status_code}")
                catalog_size1[city] = 0
        except Exception as e:
            logging.error(f"  💥 Connection error requesting size for {city}: {e!s}")
            catalog_size1[city] = 0
        
        # Polite delay between catalog size queries
        time.sleep(random.uniform(0.5, 1.5))
        
    # Validation: If the sum of all found records is 0, we should halt the process
    total_expected_records = sum(catalog_size1.values())
    logging.info(f"Total expected records to extract: {total_expected_records}")
    
    if total_expected_records > 0:
        return catalog_size1
    else:
        logging.critical("Unsuccessful catalog validation: zero records available across all target cities.")
        raise ValueError("Unsuccessful catalog validation: zero records available across all target cities.")


def extraction(pagination, header):
    logging.info("🚀 Starting full paginated data extraction...")
    all_results = []
    size = 50
    
    for city, totalhints in pagination.items():
        if totalhints == 0:
            logging.warning(f"Skipping {city.upper()} due to 0 catalog size.")
            continue
            
        logging.info(f"Starting extraction loop for: {city.upper()} ({totalhints} total records)")
        
        try:
            for offset in range(0, totalhints, size):
                url = (
                    "https://www.metrocuadrado.com/rest-search/search"
                    f"?size={size}"
                    f"&from={offset}"
                    f"&realEstateBusinessList=arriendo"
                    f"&city={city}"
                )
                response = requests.get(url, headers=header, timeout=15)
                logging.info(f"  -> [{city.upper()}] Offset {offset}/{totalhints}: Status {response.status_code}")
    
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results")
        
                    if results:
                        all_results.extend(results)
                    else:
                        logging.warning(f"  ⚠️ No results found in payload at offset {offset}")
                else:
                    logging.error(f"  ❌ Request failed at offset {offset}. Stopping pagination loop for {city.upper()}.")
                    break
    
                # Anti-ban polite delay
                time_sleep = random.uniform(1.4, 2.0)  
                logging.info(f"  💤 Sleeping for {time_sleep:.2f} seconds...")
                time.sleep(time_sleep)   
                    
        except Exception as e:
            logging.error(f"  💥 Severe connection error processing {city.upper()}: {e!s}", exc_info=True)
            
    # Raise a validation error if the extraction process yielded absolutely nothing
    if not all_results:
        logging.critical("Data extraction failed: No records retrieved for any of the target cities.")
        raise ValueError("Data extraction failed: No records retrieved for any of the target cities.")
        
    logging.info(f"Total extracted records successfully loaded into memory: {len(all_results)}")
    return all_results 
    

def storing_bronze(all_results):
    """Normalizes and safely stores collected data as a Parquet file in the Bronze Layer."""
    logging.info("Initiating DataFrame normalization and schema mapping...")
    
    # Flatten raw nested JSON lists
    df = pd.json_normalize(all_results)

    # Coerce columns to uppercase and normalize delimiters
    df.columns = [col.upper() for col in df.columns]
    df.columns = [col.replace("_", ".") for col in df.columns]
    
    logging.info(f"Initial flattened dataframe shape: {df.shape}")
    
    waited_structure = [
        'MIDINMUEBLE', 'MIDEMPRESA', 'TITLE', 'LINK', 'MBARRIO', 
        'MNOMBRECOMUNBARRIO', 'MCIUDAD.NOMBRE', 'MZONA.NOMBRE', 
        'MAREA', 'AREAPRIVADA', 'MNROCUARTOS', 'MNROBANOS', 
        'MNROGARAJES', 'ESTRATO', 'MVALORARRIENDO', 'DATA.MVALORADMINISTRACION', 
        'LOCALIZACION.LON', 'LOCALIZACION.LAT', 'MTIPOINMUEBLE.NOMBRE'
    ]
    
    try:
        # Drop duplicates at schema level
        df = df.loc[:, ~df.columns.duplicated()]
        missing_columns = [col for col in waited_structure if col not in df.columns]
        
        if missing_columns:
            logging.error(f"Schema mismatch! Missing required columns: {missing_columns}")
            raise KeyError(f"Missing required fields in source API schema: {missing_columns}") 
        
        # CORRECCIÓN: Reasignar df con el reindex
        df = df.reindex(columns=waited_structure)
        logging.info("Schema integrity and constraint validations passed successfully.")
        
    except Exception as e:
        logging.critical(f"Expected file structure check failed: {e!s}")
        raise ValueError(f"Expected data structure was not met: {e!s}")
        
    # Inject process audit metadata
    now = pd.Timestamp.now()
    df["UPLOADED_DATE"] = now
    df["LOAD_TYPE"] = "FULL"
    
    # Define system pathing using Pathlib
    BASE_DIR = Path(__file__).resolve().parent.parent
    bronze_path = BASE_DIR / "Renting_pipeline" / "Bronze" 
    bronze_path.mkdir(parents=True, exist_ok=True)
    
    # Format a unique timestamp filename
    date_str = now.strftime("%Y%m%d_%H%M%S")
    file_path = bronze_path / f"FullLoad_Col_Renting_{date_str}.parquet" 
    
    # Bulk write to disk
    df.to_parquet(file_path, index=False)
    logging.info("✅ Full load ingestion completed successfully!")
    logging.info(f"  📂 Destination File: {file_path.absolute()}")
    logging.info(f"  📊 Processed Row Count: {len(df)}")


def main():
    logging.info("--- STARTING COLOMBIA RENTING FULL ETL PIPELINE RUN ---")
    try:
        dynamic_p = catolog_size(HEADER)
        output = extraction(dynamic_p, HEADER)
        storing_bronze(output)
        logging.info("--- PIPELINE RUN COMPLETED SUCCESSFULLY ---")
    except Exception as e:
        logging.critical(f"Pipeline crashed during execution: {e!s}")


if __name__ == "__main__":
    main()