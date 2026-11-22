#!/usr/bin/env python3
"""
Phase 2: Safe Archive Extraction & Raw File Inventory Script
Extracts all raw archives into data/raw/extracted/<dataset_name>/ without modifying or deleting raw ZIPs.
"""
import os
import sys
import zipfile
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(ROOT_DIR, "data", "raw")
EXTRACTED_DIR = os.path.join(RAW_DIR, "extracted")

def inventory_raw():
    print("==========================================")
    print(" 1. INVENTORYING RAW DATASET FILES       ")
    print("==========================================")
    
    items = []
    # Search root and data/raw/ for archives
    search_paths = [ROOT_DIR, RAW_DIR]
    
    found_archives = []
    for sp in search_paths:
        for f in os.listdir(sp):
            fpath = os.path.join(sp, f)
            if os.path.isfile(fpath) and f.endswith(('.zip', '.tar', '.gz', '.xlsx', '.json', '.csv', '.pptx')):
                size_mb = os.path.getsize(fpath) / (1024 * 1024)
                found_archives.append((f, fpath, size_mb))
                
    print(f"Found {len(found_archives)} raw archive/data files:")
    for fname, fpath, size_mb in found_archives:
        print(f" - {fname} ({size_mb:.2f} MB) -> Location: {fpath}")
        
    return found_archives

def safe_extract():
    print("\n==========================================")
    print(" 2. EXTRACTING ARCHIVES SAFELY           ")
    print("==========================================")
    os.makedirs(EXTRACTED_DIR, exist_ok=True)
    
    # Map zip archives to target dataset folders
    archive_mapping = {
        "archive.zip": "indian_monuments",
        "archive (1).zip": "india_tourism_json",
        "state-wise Dataset.zip": "state_wise_tourism",
        "image_db.zip": "image_db"
    }
    
    extraction_results = {}
    
    for zip_name, target_folder in archive_mapping.items():
        # Check if zip exists in ROOT_DIR or RAW_DIR
        zip_path = os.path.join(RAW_DIR, zip_name)
        if not os.path.exists(zip_path):
            root_zip_path = os.path.join(ROOT_DIR, zip_name)
            if os.path.exists(root_zip_path):
                zip_path = root_zip_path
                
        if not os.path.exists(zip_path):
            print(f"⚠️  Archive {zip_name} not found.")
            extraction_results[zip_name] = ("Missing", 0, "File not found")
            continue
            
        target_dir = os.path.join(EXTRACTED_DIR, target_folder)
        os.makedirs(target_dir, exist_ok=True)
        
        print(f"\nProcessing {zip_name} -> {target_dir}")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Test zip integrity
                bad_file = zip_ref.testzip()
                if bad_file:
                    print(f"❌ Corrupted file found inside {zip_name}: {bad_file}")
                    extraction_results[zip_name] = ("Corrupted", 0, f"Bad file: {bad_file}")
                    continue
                    
                members = zip_ref.infolist()
                print(f"Extracting {len(members)} entries...")
                zip_ref.extractall(target_dir)
                print(f"✓ Extracted successfully to {target_dir}")
                extraction_results[zip_name] = ("Success", len(members), "OK")
                
        except zipfile.BadZipFile as bzf:
            print(f"❌ BadZipFile Error in {zip_name}: {bzf}")
            extraction_results[zip_name] = ("Corrupted Archive", 0, str(bzf))
        except Exception as exc:
            print(f"❌ Extraction error in {zip_name}: {exc}")
            extraction_results[zip_name] = ("Failed", 0, str(exc))
            
    print("\n------------------------------------------")
    print("Extraction Summary:")
    for archive, status in extraction_results.items():
        print(f" - {archive}: {status[0]} ({status[1]} entries) | {status[2]}")
    print("------------------------------------------")
    
    return extraction_results

def main():
    inventory_raw()
    safe_extract()

if __name__ == "__main__":
    main()
