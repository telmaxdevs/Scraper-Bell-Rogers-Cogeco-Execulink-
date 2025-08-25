#!/usr/bin/env python3
"""
Telmax Tools - Interactive Terminal Interface
Simple menu-driven interface to run all Telmax processing tools.
"""

import os
import sys
import subprocess
import csv
from pathlib import Path

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header."""
    print("🚀" + "="*58 + "🚀")
    print("       TELMAX EXECULINK SERVICE CHECKER")
    print("🚀" + "="*58 + "🚀")
    print()
    print("🎯 PURPOSE: Check Execulink internet availability for your addresses")
    print("📊 INPUT: telmax.csv with address data")
    print("📁 OUTPUT: Service availability results in execulink_results/")
    print()

def check_python_packages():
    """Check if required packages are installed."""
    required_packages = ['requests', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, 
                         check=True, capture_output=True)
            print("✅ Packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    else:
        print("✅ All required packages are installed.")
    
    return True

def check_csv_file(filename='telmax.csv'):
    """Check if the CSV file exists and has required columns."""
    if not os.path.exists(filename):
        return False, f"File '{filename}' not found"
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            
            if not headers:
                return False, "CSV file appears to be empty"
            
            # Check for required columns
            required_columns = ['civic_num', 'streetname', 'town']
            legacy_columns = ['AddressNumber', 'FullStreetName', 'Settlement']
            
            has_required = all(col in headers for col in required_columns)
            has_legacy = all(col in headers for col in legacy_columns)
            
            if not (has_required or has_legacy):
                missing = [col for col in required_columns if col not in headers]
                return False, f"Missing required columns: {', '.join(missing)}"
            
            # Count rows
            row_count = sum(1 for _ in reader)
            return True, f"Valid CSV with {row_count} addresses"
            
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"

def run_csv_validator():
    """Run the CSV validator."""
    print("\n🔍 Running CSV Validator...")
    print("-" * 40)
    
    if os.path.exists('validate_csv.py'):
        try:
            subprocess.run([sys.executable, 'validate_csv.py'], check=True)
        except subprocess.CalledProcessError:
            print("❌ CSV validation failed. Please fix the issues and try again.")
            return False
    else:
        # Run basic validation
        is_valid, message = check_csv_file()
        if is_valid:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            return False
    
    return True

def run_execulink_checker():
    """Run the Execulink service checker."""
    print("\n🚀 Starting Execulink Service Checker...")
    print("-" * 50)
    print("This will process all addresses in telmax.csv")
    print("Progress will be shown as the script runs.")
    print("You can press Ctrl+C to stop processing safely.")
    print()
    
    # Check if CSV file is valid first
    is_valid, message = check_csv_file()
    if not is_valid:
        print(f"❌ CSV validation failed: {message}")
        print("Please fix your CSV file before running the checker.")
        return False
    
    print(f"✅ {message}")
    print("\nStarting processing...")
    
    try:
        subprocess.run([sys.executable, 'execulink_check.py'], check=True)
        print("\n🎉 Processing completed successfully!")
        print("📁 Results saved to: execulink_results/all_results.csv")
        return True
    except subprocess.CalledProcessError:
        print("\n❌ Processing was interrupted or failed.")
        print("💡 You can restart the script - it will resume from where it left off.")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Processing stopped by user.")
        print("💡 You can restart the script - it will resume from where it left off.")
        return False

def run_data_sampler():
    """Run the data sampling tool with user input."""
    print("\n🎲 Data Sampling Tool")
    print("-" * 30)
    
    # Get input file
    input_file = input("Enter input CSV filename (default: telmax.csv): ").strip()
    if not input_file:
        input_file = "telmax.csv"
    
    if not os.path.exists(input_file):
        print(f"❌ File '{input_file}' not found")
        return False
    
    # Get sample size
    try:
        sample_size = input("Enter number of rows to sample (default: 1000): ").strip()
        if not sample_size:
            sample_size = "1000"
        sample_size = int(sample_size)
        if sample_size <= 0:
            raise ValueError("Sample size must be positive")
    except ValueError:
        print("❌ Invalid sample size. Please enter a positive number.")
        return False
    
    # Get output file
    default_output = f"sample_{input_file.replace('.csv', '')}_{sample_size}.csv"
    output_file = input(f"Enter output filename (default: {default_output}): ").strip()
    if not output_file:
        output_file = default_output
    
    try:
        cmd = [sys.executable, 'sample_difference.py', 
               '--input', input_file, 
               '--k', str(sample_size), 
               '--output', output_file]
        subprocess.run(cmd, check=True)
        print(f"✅ Sampling completed!")
        print(f"📁 Sample saved to: {output_file}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Sampling failed.")
        return False

def show_results():
    """Show information about output files."""
    print("\n📁 Output Files and Results")
    print("-" * 40)
    
    results_dir = "execulink_results"
    main_results = os.path.join(results_dir, "all_results.csv")
    
    if os.path.exists(main_results):
        try:
            with open(main_results, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                row_count = sum(1 for _ in reader)
            print(f"✅ Main results: {main_results}")
            print(f"   📊 Contains {row_count} processed addresses")
        except Exception as e:
            print(f"⚠️  Found {main_results} but couldn't read it: {e}")
    else:
        print(f"❌ Main results file not found: {main_results}")
        print("   💡 Run the Execulink checker first")
    
    # Check for other common output files
    other_files = []  # Removed difference.csv since we removed comparison feature
    for filename in other_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    row_count = sum(1 for _ in reader)
                print(f"✅ {filename} - {row_count} rows")
            except:
                print(f"✅ {filename} - file exists")
    
    # Check for sample files
    sample_files = [f for f in os.listdir('.') if f.startswith('sample_') and f.endswith('.csv')]
    if sample_files:
        print(f"✅ Sample files: {', '.join(sample_files)}")

def show_status():
    """Show current status of files and system."""
    print("\n📋 System Status")
    print("-" * 30)
    
    # Check CSV file
    is_valid, message = check_csv_file()
    if is_valid:
        print(f"✅ telmax.csv: {message}")
    else:
        print(f"❌ telmax.csv: {message}")
    
    # Check Python packages
    if check_python_packages():
        print("✅ Python packages: All required packages installed")
    else:
        print("❌ Python packages: Some packages missing")
    
    # Check output directories
    if os.path.exists("execulink_results"):
        file_count = len([f for f in os.listdir("execulink_results") if f.endswith('.csv')])
        print(f"✅ Results directory: {file_count} result files")
    else:
        print("⚠️  Results directory: Not created yet")

def show_menu():
    """Display the main menu."""
    print("\n🛠️  MAIN TOOLS:")
    print("1. Validate CSV file format")
    print("2. 🚀 RUN EXECULINK CHECKER (MAIN TOOL) 🚀")
    print("3. Sample random data from CSV")
    print("4. Show results and output files")
    print("5. Show system status")
    print("6. Exit")
    print()

def main():
    """Main interactive loop."""
    while True:
        clear_screen()
        print_header()
        show_status()
        show_menu()
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == '1':
                run_csv_validator()
            elif choice == '2':
                run_execulink_checker()
            elif choice == '3':
                run_data_sampler()
            elif choice == '4':
                show_results()
            elif choice == '5':
                show_status()
            elif choice == '6':
                print("\n👋 Thank you for using Telmax Tools!")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1-6.")
            
            if choice != '6':
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
