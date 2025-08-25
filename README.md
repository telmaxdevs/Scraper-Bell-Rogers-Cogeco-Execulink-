# Telmax Execulink Service Checker

## 🚀 START HERE 🚀

**TO RUN THIS TOOL: Double-click `START_HERE.py`**

That's it! The tool will guide you through everything else.

---

🚀 **TO START: Double-click `START_HERE.py`** 🚀

This tool checks Execulink internet service availability for a list of addresses from your CSV file.

## 🎯 Quick Start (3 Steps)

1. **Prepare your data**: Make sure you have `telmax.csv` with address columns
2. **Double-click**: `START_HERE.py` 
3. **Follow the menu**: Choose options to validate, process, and view results

## 📋 What You Need

- A CSV file named `telmax.csv` with these columns:
  - `civic_num` (street number like "123")
  - `streetname` (street name like "Main Street") 
  - `town` (city name like "Toronto")

## 📁 Your Results

Results will be saved in the `execulink_results/` folder:
- `all_results.csv` - Main output with service availability data

## Overview

The project provides tools to:
- Check Execulink internet service availability for addresses
- Compare and find differences between CSV datasets
- Sample random subsets of data for analysis
- Extract data from DWG/DXF files
- Process geographic and address information

## Prerequisites

### System Requirements
- Python 3.7 or higher
- Windows PowerShell (for some features)
- Internet connection (for API calls)

### Python Dependencies
Install the required Python packages:

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - For HTTP API calls
- `openpyxl` - For Excel file handling
- `pandas` - For data manipulation (installed automatically with openpyxl)

## Main Scripts

### 1. Execulink Service Checker (`execulink_check.py`)

**Purpose**: Checks internet service availability from Execulink for a list of addresses.

**Features**:
- Geocodes addresses using Google Maps API
- Queries Execulink's service availability API
- Processes addresses in parallel for faster execution
- Saves results to CSV files with detailed service information
- Includes backup and checkpoint functionality for large datasets

**Usage**:
```bash
python execulink_check.py
```

**How it works**:
1. Reads addresses from the `telmax.csv` file
2. Geocodes each address to get precise coordinates
3. Queries Execulink's API to check service availability
4. Saves individual results and creates consolidated output files
5. Creates checkpoints for resuming interrupted processing

**Output**: 
- Individual CSV files for each address in `execulink_results/` directory
- Consolidated results in `all_results.csv`
- Backup files and processing checkpoints

### 2. Data Sampling (`sample_difference.py`)

**Purpose**: Randomly samples a specified number of rows from a CSV file using reservoir sampling.

**Usage**:
```bash
python sample_difference.py --input telmax.csv --k 5000 --output sample_5000.csv
```

**Parameters**:
- `--input` or `-i`: Input CSV file path (default: `difference.csv`)
- `--k` or `-k`: Number of rows to sample (default: 12000)
- `--output` or `-o`: Output CSV file path (default: `sample_difference_12000.csv`)
- `--seed`: Random seed for reproducible results (optional)

**Example**:
```bash
# Sample 5000 random rows from telmax.csv
python sample_difference.py --input telmax.csv --k 5000 --output sample_5000.csv

# Sample with reproducible results
python sample_difference.py --input data.csv --k 1000 --output sample.csv --seed 42
```

## Required Input File Format

### CSV File Requirements (`telmax.csv`)

The main script expects a CSV file named `telmax.csv` in the project root directory with the following **required columns**:

#### Essential Columns (Required for Execulink Checker):
- `civic_num`: The street number (e.g., "123", "456")
- `streetname`: The street name (e.g., "Main Street", "Oak Avenue") 
- `town`: The city/town name (e.g., "Toronto", "Burlington")

#### Example CSV Format:
```csv
civic_num,streetname,town,postal_code,da,fdh_id
123,Main Street,Toronto,M1A 1A1,295,295-97
456,Oak Avenue,Burlington,L7L 1L1,133,133-45
789,Pine Road,Richmond Hill,L4E 1B2,402,402-23
```

#### Legacy Column Support:
The script also supports older column names for backward compatibility:
- `AddressNumber` (instead of `civic_num`)
- `FullStreetName` (instead of `streetname`)
- `Settlement` (instead of `town`)

### Data Files

### Input Files
- `telmax.csv`: **Main dataset** - Must contain address columns listed above
- `telmax1.csv`: Secondary dataset for comparison (used by `finddif.py`)

### Output Files
- `execulink_results/`: Directory containing individual address results
- `execulink_results/all_results.csv`: **Main output** - Consolidated Execulink service check results
- `difference.csv`: Differences between telmax datasets
- `sample_difference_*.csv`: Random samples of data

### What's in the Output File (`all_results.csv`):
The main results file contains your original address data plus:
- **Geocoding results**: Exact latitude/longitude coordinates
- **Service availability**: Whether Execulink serves the address  
- **Connection details**: Available internet speeds and plans
- **Infrastructure info**: Technical details about fiber availability
- **Pricing data**: Available service plans and costs
- **Original address**: The address as processed by the script

Example output columns:
```csv
original_address,geocoded_latitude,geocoded_longitude,serviceAvailable,connectionType,speeds,monthlyRate,...
"123 Main St, Toronto, ON",43.6532,-79.3832,true,fiber,"100/10,500/50",49.99,...
```

## Helper Tools

### Interactive Terminal Interface (`telmax_terminal.py`) ⭐ **Recommended**
**Purpose**: All-in-one menu-driven interface for all tools.

**Usage**:
```bash
python telmax_terminal.py
```

**Features**:
- 🎯 Simple menu interface - no command line knowledge needed
- ✅ Automatic dependency installation and checking
- 📊 Real-time system status and file validation
- 🔄 Resume interrupted processing automatically
- 📁 Easy results viewing and file management
- ❌ Clear error messages with solutions
- 🛠️ Access to all tools in one place

**Menu Options**:
1. **Validate CSV** - Check file format before processing
2. **Run Execulink Checker** - Main address processing tool
3. **Sample Data** - Create random samples from large datasets
4. **Show Results** - View output files and statistics
5. **System Status** - Check files, dependencies, and setup

### CSV Validator (`validate_csv.py`)
**Purpose**: Checks if your CSV file has the correct format before running the main script.

**Usage**:
```bash
python validate_csv.py
```

**What it checks**:
- File exists and is readable
- Has required columns (civic_num, streetname, town)
- Shows sample addresses from your file
- Identifies missing data issues
- Provides helpful formatting guidance

**Example output**:
```
📁 Checking file: telmax.csv
📋 Found columns: civic_num, streetname, town, postal_code
✅ All required columns found
📝 Sample address 1: 123 Main Street, Toronto
📊 Total addresses in file: 1,250
✅ File validation passed! Ready to run execulink checker.
```

### Batch File (`run_execulink_check.bat`)
**Purpose**: One-click execution with automatic setup.

**Features**:
- Checks for telmax.csv file
- Verifies Python installation
- Installs dependencies automatically
- Runs the Execulink checker
- Shows clear error messages if issues occur

**Usage**: Simply double-click the file in Windows Explorer.

## Quick Start Guide

### Method 1: Interactive Terminal Interface (Recommended ⭐)

The easiest way to use all the tools with a simple menu-driven interface:

```bash
python telmax_terminal.py
```

**Features**:
- 🎯 User-friendly menu with all tools
- ✅ Automatic validation and dependency checking
- 📊 Real-time status updates
- 🔄 Resume interrupted processing
- 📁 Easy results viewing
- ❌ Clear error messages and solutions

**What you'll see**:
```
==========================================================
           TELMAX ADDRESS PROCESSING TOOLS
==========================================================

📋 System Status
✅ telmax.csv: Valid CSV with 1,250 addresses
✅ Python packages: All required packages installed
✅ Results directory: 0 result files

🛠️  Available Tools:
1. Validate CSV file format
2. Run Execulink service checker (main tool)
3. Sample random data from CSV
4. Show results and output files
5. Show system status
6. Exit

Enter your choice (1-6):
```

### Method 2: Simple Double-Click Execution

1. **Prepare your data**: Make sure you have a file named `telmax.csv` with the required columns (see format below)

2. **Validate your CSV** (optional but recommended):
   ```bash
   python validate_csv.py
   ```
   This will check if your CSV file has the correct format and show examples.

3. **Run the batch file**: Double-click `run_execulink_check.bat` 
   - Automatically checks for Python and dependencies
   - Installs missing packages if needed  
   - Runs the Execulink checker
   - Shows progress and results

### Method 3: Command Line

1. **Open Command Prompt or PowerShell** in the project directory

2. **Install dependencies** (first time only):
   ```bash
   pip install -r requirements.txt
   ```

3. **Validate your CSV file** (recommended):
   ```bash
   python validate_csv.py
   ```

4. **Run the main script**:
   ```bash
   python execulink_check.py
   ```

### What Happens When You Run It:
- The script reads addresses from `telmax.csv`
- Shows progress in real-time (e.g., "Progress: 50/1000 processed")
- Creates individual result files for each address
- Saves consolidated results to `execulink_results/all_results.csv`
- Can be safely interrupted and resumed (uses checkpoints)
- Typically processes 20-30 addresses per minute

## Running the Scripts

### Step-by-Step Process

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare Your Data**:
   - Ensure `telmax.csv` contains your address data with required columns
   - Place the file in the same directory as the scripts

3. **Check Execulink Service Availability**:
   ```bash
   python execulink_check.py
   ```
   - This will process all addresses in `telmax.csv`
   - Results will be saved in `execulink_results/` directory
   - Progress will be displayed in the terminal
   - **Processing time**: Expect ~2-3 minutes per 100 addresses

4. **Sample Data** (if needed):
   ```bash
   python sample_difference.py --input your_file.csv --k 1000 --output sample_output.csv
   ```

## Configuration and Customization

### API Keys
The Execulink checker uses a Google Maps API key for geocoding. The key is currently hardcoded in the script. For production use, consider:
- Moving the API key to an environment variable
- Implementing proper API key management

### Parallel Processing
The Execulink checker uses multithreading to process addresses faster. You can adjust the number of threads by modifying the `max_workers` parameter in the script.

### Output Formats
All scripts output to CSV format by default. You can modify the scripts to support other formats like JSON or Excel if needed.

## Troubleshooting

### CSV File Issues

**Problem**: "ERROR: telmax.csv file not found!"
- **Solution**: Make sure you have a file named exactly `telmax.csv` in the same folder as the scripts

**Problem**: "Missing required columns"
- **Solution**: Your CSV must have these exact column names: `civic_num`, `streetname`, `town`
- **Alternative**: Use legacy column names: `AddressNumber`, `FullStreetName`, `Settlement`

**Problem**: "No valid addresses found"
- **Solution**: Make sure each row has values in all three required columns
- Check for empty cells or missing data
- Run `python validate_csv.py` to see specific issues

**Problem**: Special characters in addresses
- **Solution**: Save your CSV with UTF-8 encoding
- Avoid special characters like quotes within address fields

### Example CSV File Creation:
If you have address data in Excel:
1. Arrange columns: civic_num, streetname, town
2. Fill in all required fields
3. Save As → CSV (UTF-8)
4. Name the file `telmax.csv`

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

2. **API Rate Limiting**: If you encounter rate limiting errors:
   - The script includes automatic delays and retry logic
   - Consider increasing delay times in the code if needed

3. **Large Dataset Processing**: 
   - The Execulink checker includes checkpoint functionality
   - If processing is interrupted, you can resume from the last checkpoint

4. **Memory Issues**: 
   - For very large datasets, consider processing in smaller batches
   - Use the sampling tool to work with smaller subsets first

### Error Messages
- "No geocoding results found": Address couldn't be located by Google Maps
- "No api_attributes found": Execulink API didn't return service information
- "Error processing address": General processing error, check address format

## Contributing

When modifying the scripts:
1. Test with small datasets first
2. Maintain the CSV output format for compatibility
3. Add appropriate error handling for new features
4. Update this README with any new functionality

## Notes

- The scripts are designed to work with the specific data structure of Telmax CSV files
- Processing large datasets may take considerable time due to API rate limits
- Always backup your data before running batch processing operations
- Some features require internet connectivity for API calls
