import os
import glob
import pandas as pd
import json
from typing import List, Dict, Any
from tqdm import tqdm

from utils import logger
from search import search_person
from extractor import scrape_url_content
from llm_parser import parse_intel_with_llm

def find_input_file() -> str:
    """Finds the first valid CSV or Excel file in the input directory."""
    supported_extensions = ["*.csv", "*.xlsx"]
    found_files = []
    for ext in supported_extensions:
        found_files.extend(glob.glob(os.path.join("input", ext)))
    
    if not found_files:
        raise FileNotFoundError("No input CSV or XLSX data found within the '/input' directory.")
    return found_files[0]

def load_input_data(file_path: str) -> pd.DataFrame:
    """Loads input file data into a normalized Pandas DataFrame."""
    logger.info(f"Loading incoming processing queue records from: {file_path}")
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
        
    # Match schema expectations
    required = ['Name', 'Graduation Year']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing mandatory column: '{col}' from input file context mapping.")
            
    return df

def run_pipeline():
    """Orchestrates data operations for the NSD Graduate ingestion engine."""
    logger.info("Initializing NSD Graduate Intel Pipeline Engine...")
    
    try:
        input_file = find_input_file()
        df = load_input_data(input_file)
    except Exception as e:
        logger.critical(f"Pipeline structural initiation aborted: {e}")
        return

    final_processed_dataset: List[Dict[str, Any]] = []
    
    # Iterate safely across target items
    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing Graduates Pipeline"):
        name = str(row['Name']).strip()
        year = row['Graduation Year']
        
        if not name or pd.isna(row['Name']):
            continue
            
        logger.info(f"Processing candidate entity: {name} (Graduation: {year})")
        
        # Step 1: Query Discovery
        discovered_leads = search_person(name, year)
        logger.info(f"Discovered {len(discovered_leads)} potential online lead sources for {name}")
        
        # Step 2: Content Gathering
        valid_evidence_store = []
        # Limit processing depth to top 6 relevant web sources to maintain pipeline performance
        for lead in discovered_leads[:6]:
            url = lead['url']
            extracted_text = scrape_url_content(url)
            
            if extracted_text:
                lead['page_text'] = extracted_text
                valid_evidence_store.append(lead)
                
        # Step 3: LLM Parsing and Structural Processing
        structured_profile = parse_intel_with_llm(name, year, valid_evidence_store)
        
        # Enforce accuracy on keys provided by the source input list data
        structured_profile['name'] = name
        structured_profile['graduation_year'] = str(year)
        
        final_processed_dataset.append(structured_profile)
        
    # Step 4: Write Outputs across Formats
    write_output_files(final_processed_dataset)
    logger.info("NSD Graduate Discovery Pipeline completed operations successfully.")

def write_output_files(dataset: List[Dict[str, Any]]):
    """Outputs matching representations for JSON, CSV, and XLSX formats."""
    if not dataset:
        logger.warning("No generated output data records were produced to be saved.")
        return
        
    out_df = pd.DataFrame(dataset)
    
    # Convert lists to strings for flat-file formats (CSV/Excel)
    flat_df = out_df.copy()
    for col in flat_df.columns:
        if flat_df[col].apply(lambda x: isinstance(x, list)).any():
            flat_df[col] = flat_df[col].apply(lambda val: ", ".join(val) if isinstance(val, list) else val)

    # Save CSV
    csv_path = os.path.join("output", "nsd_profiles.csv")
    flat_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    # Save Excel
    excel_path = os.path.join("output", "nsd_profiles.xlsx")
    flat_df.to_excel(excel_path, index=False)
    
    # Save JSON
    json_path = os.path.join("output", "nsd_profiles.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Data outputs generated at: {os.path.abspath('output')}")

if __name__ == "__main__":
    run_pipeline()