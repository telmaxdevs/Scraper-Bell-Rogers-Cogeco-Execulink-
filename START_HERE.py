#!/usr/bin/env python3
"""
🚀 TELMAX EXECULINK CHECKER - START HERE 🚀

This is the MAIN FILE to run the Telmax address processing tool.

BEFORE RUNNING:
1. Make sure you have a file called 'telmax.csv' with your addresses
2. Your CSV must have these columns: civic_num, streetname, town

TO RUN THIS TOOL:
Double-click this file OR run: python START_HERE.py

This will open an easy-to-use menu where you can:
✅ Validate your CSV file
✅ Check Execulink service for all addresses
✅ View results
✅ Get help with any issues
"""

import os
import sys
import subprocess

def main():
    print("🚀" + "="*60 + "🚀")
    print("    TELMAX EXECULINK CHECKER - MAIN INTERFACE")
    print("🚀" + "="*60 + "🚀")
    print()
    print("📋 This tool checks Execulink internet service availability")
    print("   for a list of addresses in your CSV file.")
    print()
    print("📁 Required: A file called 'telmax.csv' with columns:")
    print("   - civic_num (street number)")
    print("   - streetname (street name)")  
    print("   - town (city/town name)")
    print()
    print("🔥 STARTING MAIN INTERFACE...")
    print()
    
    # Check if the terminal interface exists
    if os.path.exists('telmax_terminal.py'):
        try:
            subprocess.run([sys.executable, 'telmax_terminal.py'], check=True)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("💡 Try running: python telmax_terminal.py")
    else:
        print("❌ Main interface file not found!")
        print("💡 Make sure 'telmax_terminal.py' is in the same folder")

if __name__ == "__main__":
    main()
