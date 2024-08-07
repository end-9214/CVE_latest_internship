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

def delete_files_in_directory(directory):
    """Delete all files in a directory."""
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
    except Exception as e:
        print(f"Error deleting files in {directory}: {e}")

while True:
    # Step 1: Run the latest files download script
    run_script(download_script_path)
    
    # Step 2: Run the keyword search script
    run_script(search_script_path)
    
    # Step 3: Wait for 2 hours
    print("Waiting for 2 hours...")
    time.sleep(2 * 3600)  # Sleep for 2 hours (7200 seconds)
    
    # Step 4: Delete all files in the Found_Keyword_files directory
    delete_files_in_directory(found_keyword_dir)
    
    # Optional: You can add a check to ensure the directory is empty if needed
    if not os.listdir(found_keyword_dir):
        print("Found_Keyword_files directory is empty. Restarting the process.")
    else:
        print("Found_Keyword_files directory is not empty. Please check manually.")
