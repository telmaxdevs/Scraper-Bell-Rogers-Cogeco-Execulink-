import requests
import json
import urllib.parse
import csv
import os
import time
import random
from datetime import datetime
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Step 1: Geocode the address ---
def geocode_address(address_string):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address_string,
        'key': 'AIzaSyCrjghe4FB5fzJps7L5P9TK5-E8po8QiQg',
    }

    # Add a small delay to avoid rate limiting
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        # Check if we got results
        if not data.get("results"):
            print(f"⚠️ No geocoding results found for address: {address_string}")
            return None
            
        result = data["results"][0]
        loc = result["geometry"]["location"]
        comps = {t: c["long_name"] for c in result["address_components"] for t in c["types"]}
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error geocoding address {address_string}: {str(e)}")
        return None

    return {
        "address_number": comps.get("street_number", ""),
        "address_name": comps.get("route", ""),
        "city": comps.get("locality", comps.get("neighborhood", "")),
        "province": comps.get("administrative_area_level_1", ""),
        "address_postal": comps.get("postal_code", ""),
        "latitude": loc["lat"],
        "longitude": loc["lng"]
    }

# --- Step 2: Build the location cookie ---
def build_location_cookie(address_data):
    return urllib.parse.quote(urllib.parse.quote(json.dumps(address_data)))

# --- Step 3: Make the request to Execulink and get response cookies ---
def fetch_execulink_cookies(location_cookie):
    url = 'https://www.execulink.ca/residential/internet/?location=new'
    cookies = {"location": location_cookie}
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 CrKey/1.54.250320'
    }

    # Add a small delay to avoid rate limiting    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=15)
        response.raise_for_status()
        return response.cookies.get_dict()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching from Execulink: {str(e)}")
        return {}

# --- Step 4: Decode api_attributes and save CSV ---
def save_api_attributes_csv(response_cookies, original_address, output_directory='execulink_results', csv_filename=None):
    if 'api_attributes' not in response_cookies:
        print(f"⚠️ No api_attributes found in response cookies for address: {original_address}")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        
    # Use a sanitized version of address for filename if not provided
    if csv_filename is None:
        sanitized_address = original_address.replace(' ', '_').replace(',', '').replace('.', '')
        csv_filename = f"{sanitized_address}_execulink_data.csv"
    
    output_path = os.path.join(output_directory, csv_filename)

    # Double URL-decode
    decoded = urllib.parse.unquote(urllib.parse.unquote(response_cookies['api_attributes']))
    attributes = json.loads(decoded)

    # Add original address
    attributes['original_address'] = original_address

    # Write to CSV (keys as headers)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=attributes.keys())
        writer.writeheader()
        writer.writerow(attributes)

    print(f"✅ Saved CSV to {output_path}")

# --- Function to process a single address ---
def process_single_address(address_data, results_dir, thread_id):
    """Process a single address and return the result"""
    try:
        address_number, street_name, settlement, row_index = address_data
        
        # Format the address string
        address_string = f"{address_number} {street_name}, {settlement}, ON"
        print(f"🔍 Thread {thread_id}: Processing address ({row_index}): {address_string}")
        
        # Geocode the address
        addr_data = geocode_address(address_string)
        if not addr_data:
            return None
        
        # Build location cookie
        location_cookie = build_location_cookie(addr_data)
        
        # Fetch Execulink cookies
        response_cookies = fetch_execulink_cookies(location_cookie)

        # Do not save individual files here. Return structured attributes for batching.
        if 'api_attributes' in response_cookies:
            decoded = urllib.parse.unquote(urllib.parse.unquote(response_cookies['api_attributes']))
            attributes = json.loads(decoded)
            attributes['original_address'] = address_string
            attributes['row_index'] = row_index
            # Add geocoded coordinates
            attributes['geocoded_latitude'] = addr_data['latitude']
            attributes['geocoded_longitude'] = addr_data['longitude']
            return attributes
        else:
            print(f"⚠️ Thread {thread_id}: No api_attributes found for {address_string}")
            return None
            
    except Exception as e:
        print(f"❌ Thread {thread_id}: Error processing {address_data}: {str(e)}")
        return None

# --- Function to save temporary backup ---
def save_backup_csv(results, results_dir, batch_number):
    """Save a backup of results to CSV in the results directory"""
    if not results:
        return

    temp_file = os.path.join(results_dir, f'temp_backup_{batch_number}.csv')

    # Determine full fieldnames across results
    all_fieldnames = set()
    for r in results:
        all_fieldnames.update(r.keys())
    fieldnames = sorted(list(all_fieldnames))

    with open(temp_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"💾 Saved CSV backup: {temp_file}")

# --- Function to load existing results ---
def load_existing_results(master_results_file):
    """Load existing results from master file"""
    existing_results = []
    processed_indices = set()
    
    if os.path.exists(master_results_file):
        try:
            with open(master_results_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_results.append(row)
                    if 'row_index' in row:
                        processed_indices.add(int(row['row_index']))
        except Exception as e:
            print(f"⚠️ Error reading existing results: {e}")
    
    return existing_results, processed_indices

# --- Main ---
if __name__ == "__main__":
    # Configuration
    # Use the telmax CSV (supports new column names). Falls back to previous names if present.
    input_csv = 'telmax.csv'
    results_dir = 'execulink_results'
    # store temp batch Excel files in the execulink_results folder as requested
    temp_dir = results_dir
    max_workers = 25  # Increased from 3 to 8 for faster processing
    backup_interval = 50  # Back to 50 addresses per batch
    
    # Create results directory if it doesn't exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # File paths
    master_results_file = os.path.join(results_dir, 'all_results.csv')
    checkpoint_file = os.path.join(results_dir, 'checkpoint.txt')
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"🚀 Starting multi-threaded processing at {timestamp}")
    print(f"🧵 Using {max_workers} threads")
    print(f"� Backup interval: every {backup_interval} addresses")
    
    # Load existing results and find processed indices
    existing_results, processed_indices = load_existing_results(master_results_file)
    print(f"📋 Found {len(existing_results)} existing results")
    
    # Read all addresses from CSV
    addresses_to_process = []
    with open(input_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for i, row in enumerate(reader):
            # Skip if already processed
            if i + 1 in processed_indices:
                continue
                
            # New telmax column names: civic_num, streetname, town
            # Fall back to original names if telmax uses the old schema.
            address_number = row.get('civic_num', row.get('AddressNumber', ''))
            street_name = row.get('streetname', row.get('FullStreetName', ''))
            settlement = row.get('town', row.get('Settlement', ''))
            
            if address_number and street_name and settlement:
                addresses_to_process.append((address_number, street_name, settlement, i + 1))
            else:
                print(f"⚠️ Skipping row {i+2}: Missing required address components")
    
    total_addresses = len(addresses_to_process)
    print(f"📊 Addresses to process: {total_addresses}")
    
    if total_addresses == 0:
        print("✅ All addresses have been processed!")
        exit(0)
    
    # Process addresses in batches using thread pool
    all_results = existing_results.copy()
    batch_results = []
    processed_count = 0
    successful_count = len(existing_results)
    batch_number = 1
    
    # Process addresses with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_address = {
            executor.submit(process_single_address, addr_data, results_dir, i % max_workers): addr_data 
            for i, addr_data in enumerate(addresses_to_process)
        }
        
        # Process completed tasks
        for future in as_completed(future_to_address):
            try:
                result = future.result()
                processed_count += 1
                
                if result is not None:
                    batch_results.append(result)
                    all_results.append(result)
                    successful_count += 1
                
                # When we have backup_interval results collected, update master CSV
                if len(batch_results) >= backup_interval:
                    # Update master file (CSV) with new batch - get all fieldnames dynamically
                    with open(master_results_file, 'w', newline='', encoding='utf-8') as f:
                        if all_results:
                            # Get all possible fieldnames from all results
                            all_fieldnames = set()
                            for result in all_results:
                                all_fieldnames.update(result.keys())
                            fieldnames = sorted(list(all_fieldnames))
                            
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(all_results)

                    print(f"📈 Progress: {processed_count}/{total_addresses} processed ({successful_count} successful)")
                    batch_results = []
                    batch_number += 1

                # Also save a larger CSV backup every 500 processed
                if processed_count > 0 and processed_count % 500 == 0:
                    save_backup_csv(all_results, results_dir, processed_count // 500)
                
                # Print progress every 10 addresses
                if processed_count % 10 == 0:
                    print(f"📈 Progress: {processed_count}/{total_addresses} processed ({successful_count} successful)")
                    
            except Exception as e:
                print(f"❌ Error processing future: {str(e)}")
    
    # Save final batch if any remaining (write master CSV and a final backup if large)
    if batch_results:
        # write master CSV
        with open(master_results_file, 'w', newline='', encoding='utf-8') as f:
            if all_results:
                all_fieldnames = set()
                for result in all_results:
                    all_fieldnames.update(result.keys())
                fieldnames = sorted(list(all_fieldnames))
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_results)

    # Save a final CSV backup if we processed 500+ addresses in total
    if processed_count >= 500:
        save_backup_csv(all_results, results_dir, (processed_count // 500) + 1)
    
    # Write final master results file
    with open(master_results_file, 'w', newline='', encoding='utf-8') as f:
        if all_results:
            # Get all possible fieldnames from all results
            all_fieldnames = set()
            for result in all_results:
                all_fieldnames.update(result.keys())
            fieldnames = sorted(list(all_fieldnames))
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
    
    print(f"\n🎉 Processing complete!")
    print(f"📊 Total processed: {processed_count}/{total_addresses}")
    print(f"✅ Successful: {successful_count}")
    print(f"📁 Results saved to {master_results_file}")
    print(f"💾 Temporary backups saved to {temp_dir}")
    
    # Clean up checkpoint file
    if os.path.exists(checkpoint_file):
        os.remove(checkpoint_file)
