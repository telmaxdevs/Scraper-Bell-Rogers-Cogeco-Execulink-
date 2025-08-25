#!/usr/bin/env python3
"""
CSV Validator for Execulink Checker
Validates that your CSV file has the required columns and format.
"""

import csv
import sys
import os

def validate_csv(filename='telmax.csv'):
    """Validate the CSV file format and required columns."""
    
    if not os.path.exists(filename):
        print(f"❌ ERROR: File '{filename}' not found!")
        print("\nRequired: Create a CSV file named 'telmax.csv' with your address data.")
        return False
    
    print(f"📁 Checking file: {filename}")
    
    # Required columns
    required_columns = ['civic_num', 'streetname', 'town']
    legacy_columns = {
        'civic_num': ['AddressNumber'],
        'streetname': ['FullStreetName'], 
        'town': ['Settlement']
    }
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            
            if not headers:
                print("❌ ERROR: CSV file appears to be empty or invalid!")
                return False
            
            print(f"📋 Found columns: {', '.join(headers)}")
            
            # Check for required columns
            missing_columns = []
            found_columns = []
            
            for req_col in required_columns:
                if req_col in headers:
                    found_columns.append(req_col)
                else:
                    # Check for legacy column names
                    legacy_found = False
                    for legacy_col in legacy_columns.get(req_col, []):
                        if legacy_col in headers:
                            found_columns.append(f"{legacy_col} (legacy)")
                            legacy_found = True
                            break
                    
                    if not legacy_found:
                        missing_columns.append(req_col)
            
            if missing_columns:
                print(f"❌ ERROR: Missing required columns: {', '.join(missing_columns)}")
                print("\nRequired columns:")
                for col in required_columns:
                    legacy_info = f" (or {', '.join(legacy_columns[col])})" if col in legacy_columns else ""
                    print(f"  - {col}{legacy_info}")
                return False
            
            print(f"✅ All required columns found: {', '.join(found_columns)}")
            
            # Check first few rows for data
            row_count = 0
            valid_rows = 0
            sample_issues = []
            
            for i, row in enumerate(reader):
                row_count += 1
                if row_count > 5:  # Check only first 5 rows for sample
                    break
                
                # Check if row has required data
                civic_num = row.get('civic_num', row.get('AddressNumber', '')).strip()
                streetname = row.get('streetname', row.get('FullStreetName', '')).strip()
                town = row.get('town', row.get('Settlement', '')).strip()
                
                if civic_num and streetname and town:
                    valid_rows += 1
                    if i < 3:  # Show first 3 valid examples
                        print(f"📝 Sample address {i+1}: {civic_num} {streetname}, {town}")
                else:
                    issue = f"Row {i+2}: Missing data - "
                    missing = []
                    if not civic_num: missing.append("civic_num")
                    if not streetname: missing.append("streetname") 
                    if not town: missing.append("town")
                    issue += ", ".join(missing)
                    sample_issues.append(issue)
            
            # Count total rows
            csvfile.seek(0)
            next(csv.reader(csvfile))  # Skip header
            total_rows = sum(1 for _ in csv.reader(csvfile))
            
            print(f"📊 Total addresses in file: {total_rows}")
            
            if sample_issues:
                print(f"⚠️  Issues found in sample rows:")
                for issue in sample_issues[:3]:  # Show max 3 issues
                    print(f"   {issue}")
                if len(sample_issues) > 3:
                    print(f"   ... and {len(sample_issues) - 3} more issues")
                print("\n💡 Make sure all rows have values for civic_num, streetname, and town columns")
            
            if valid_rows > 0:
                print(f"✅ File validation passed! Found {valid_rows} valid sample addresses.")
                print("\n🚀 Ready to run: python execulink_check.py")
                print("   Or double-click: run_execulink_check.bat")
                return True
            else:
                print("❌ ERROR: No valid addresses found in sample rows!")
                return False
                
    except Exception as e:
        print(f"❌ ERROR reading CSV file: {str(e)}")
        return False

def show_csv_example():
    """Show an example of the required CSV format."""
    print("\n📋 Example CSV format for 'telmax.csv':")
    print("=" * 50)
    print("civic_num,streetname,town,postal_code")
    print("123,Main Street,Toronto,M1A 1A1")
    print("456,Oak Avenue,Burlington,L7L 1L1") 
    print("789,Pine Road,Richmond Hill,L4E 1B2")
    print("=" * 50)
    print("\nRequired columns:")
    print("- civic_num: Street number (e.g., 123)")
    print("- streetname: Street name (e.g., Main Street)")
    print("- town: City/town name (e.g., Toronto)")
    print("\nOptional columns (will be preserved):")
    print("- postal_code, da, fdh_id, province, etc.")

if __name__ == "__main__":
    print("🔍 Telmax CSV Validator")
    print("=" * 40)
    
    filename = 'telmax.csv'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    
    if not validate_csv(filename):
        show_csv_example()
        print(f"\n💡 Fix the issues above and run again: python validate_csv.py")
        sys.exit(1)
    else:
        print("\n🎉 Your CSV file is ready to use!")
