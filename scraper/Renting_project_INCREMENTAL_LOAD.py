import logging
import os
import random
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"
print(SCRIPT_DIR)

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    HEADER = {
    "x-api-key": os.getenv("API_KEY"),
    "User-Agent": os.getenv("USER_AGENT")
}
    
else:
    logging.critical("⚠️ .env file not found! Unable to initialize headers.")
    raise ValueError("API credentials not found!")

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("Incremental_ingestion.log",encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def data_extraction(header):
    cities = [
        "medellin", "bogota", "cali", "itagui", "la-estrella", "sabaneta", "caldas", "bello",
        "barranquilla", "cartagena-de-indias", "bucaramanga", "soacha", "cucuta", "pereira",
        "manizales", "ibague", "santa-marta"
    ]
    
    incremental_results = []
    size = 50  # Fetching maximum chunk size for page 1
    
    logging.info("🚀 Starting incremental data extraction (Page 1)...")
    start_time = time.time()
    
    for city in cities:
        try:
            logging.info(f"Extracting data for city: {city}...")
            
            url = (
                "https://www.metrocuadrado.com/rest-search/search"
                f"?size={size}"
                f"&from=0" 
                f"&realEstateBusinessList=arriendo"
                f"&city={city}"
            )
            response = requests.get(url, headers=header, timeout=10)
            
            if response.status_code == 200:
                logging.info(f"  -> [{city}] Status: {response.status_code}")
                data = response.json()
                results = data.get("results")
                if results:
                    incremental_results.extend(results)
                    logging.info(f"  -> [{city}] Successfully retrieved {len(results)} records")
                else:
                    logging.warning(f"  -> [{city}] Status 200 but returned empty results")
            else:
                logging.warning(f"  ❌ Error fetching {city}: HTTP {response.status_code}")
                
        except Exception as e:
            logging.error(f"  💥 Extraction failed for {city}: {e!s}", exc_info=True)
        
        # API delay request  
        time.sleep(random.uniform(0.8, 1.8))
        
    execution_time = round(time.time() - start_time, 2)
    logging.info(f"Extraction execution completed in {execution_time} seconds.")
    
    if incremental_results:
        logging.info(f"Total accumulated records from extraction: {len(incremental_results)}")
        return incremental_results
    else:
        logging.critical("Unsuccessful data ingestion: no records retrieved for any city.")
        raise ValueError("Unsuccessful data ingestion: no records retrieved for any city.")


def saving_incremental_parquet(results):
    """Normalizes, validates against target schema, and saves daily delta as an immutable Parquet file."""
    logging.info("Initiating DataFrame normalization and structuring process...")
    
    # 1. Flatten base JSON structure
    df = pd.json_normalize(results)
    df.columns = [col.upper() for col in df.columns]
    
    logging.info(f"Initial flattened dataframe shape: {df.shape}")

    # 2. Manual dictionary field extraction based on target schema
    if 'MCIUDAD' in df.columns:
        df['MCIUDAD.NOMBRE'] = df['MCIUDAD'].apply(lambda x: x.get('nombre') if isinstance(x, dict) else None)
    
    if 'MZONA' in df.columns:
        df['MZONA.NOMBRE'] = df['MZONA'].apply(lambda x: x.get('nombre') if isinstance(x, dict) else None)
        
    if 'LOCALIZACION' in df.columns:
        df['LOCALIZACION.LON'] = df['LOCALIZACION'].apply(lambda x: x.get('lon') if isinstance(x, dict) else None)
        df['LOCALIZACION.LAT'] = df['LOCALIZACION'].apply(lambda x: x.get('lat') if isinstance(x, dict) else None)
        
    if 'DATA' in df.columns:
        df['DATA.MVALORADMINISTRACION'] = df['DATA'].apply(lambda x: x.get('mvaloradministracion') if isinstance(x, dict) else None)
    
    waited_structure = [
        'MIDINMUEBLE', 'MIDEMPRESA', 'TITLE', 'LINK', 'MBARRIO', 
        'MNOMBRECOMUNBARRIO', 'MCIUDAD.NOMBRE', 'MZONA.NOMBRE', 
        'MAREA', 'AREAPRIVADA', 'MNROCUARTOS', 'MNROBANOS', 
        'MNROGARAJES', 'ESTRATO', 'MVALORARRIENDO', 'DATA.MVALORADMINISTRACION', 
        'LOCALIZACION.LON', 'LOCALIZACION.LAT', 'MTIPOINMUEBLE.NOMBRE'
    ]
    
    try:
        # Remove duplicate column names if any
        df = df.loc[:, ~df.columns.duplicated()]
        
        missing_columns = [col for col in waited_structure if col not in df.columns]
        if missing_columns:
            logging.error(f"Target schema mismatch. Missing fields: {missing_columns}")
            raise KeyError(f"Missing required fields in source API schema: {missing_columns}")
             
        df = df.reindex(columns=waited_structure)
        logging.info("Schema integrity validated successfully against target structure.")
        
    except Exception as e:
        logging.critical(f"Schema validation failed: {e!s}")
        raise ValueError(f"Expected data structure was not met: {e!s}")
        
    # Set Bronze file paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    bronze_path = BASE_DIR / "Renting_pipeline" / "Bronze"
    
    if not bronze_path.exists():
        logging.info(f"Creating missing directory: {bronze_path}")
        bronze_path.mkdir(parents=True, exist_ok=True)
    
    # Add extraction and load metadata
    now = pd.Timestamp.now()
    df["UPLOADED_DATE"] = now
    df["LOAD_TYPE"] = "INCREMENTAL"
    
    date_str = now.strftime("%Y%m%d_%H%M%S")
    file_path = bronze_path / f"Incremental_Col_Renting_{date_str}.parquet"
    
    # Write to local storage
    df.to_parquet(file_path, index=False)
    logging.info("✅ Incremental file ingestion completed successfully!")
    logging.info(f" 📂 File written: {file_path.absolute()}")
    logging.info(f" 📊 Processed Row Count: {len(df)}")


def main():
    logging.info("--- STARTING COLOMBIA RENTING ETL PIPELINE RUN ---")
    try:
        new_data = data_extraction(HEADER)
        saving_incremental_parquet(new_data)
        logging.info("--- PIPELINE EXECUTION FINISHED SUCCESSFULLY ---")
    except Exception as e:
        logging.critical(f"Pipeline execution crashed: {e!s}")


if __name__ == "__main__":
    main()