import subprocess
import time
import os

# Define paths to scripts and directories
download_script_path = '/workspaces/codespaces-blank/Latest_files_download_script.py'
search_script_path = '/workspaces/codespaces-blank/keyword_search_script.py'
found_keyword_dir = '/workspaces/codespaces-blank/Found_Keyword_files'

def run_script(script_path):
    """Run a Python script using subprocess."""
    try:
        subprocess.run(['python', script_path], check=True)
        print(f"Successfully ran {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}: {e}")


while True:
    # Step 1: Run the latest files download script
    run_script(download_script_path)
    
    # Step 2: Run the keyword search script
    run_script(search_script_path)
    
    # Step 3: Wait for 20 seconds
    print("Waiting for 20 seconds...")
    time.sleep(4*3600) 

