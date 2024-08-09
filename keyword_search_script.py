import os
import json
import shutil
import csv

# Define directories
latest_files_dir = '/workspaces/codespaces-blank/latest_files'
found_keyword_dir = '/workspaces/codespaces-blank/Found_Keyword_files'
keywords_csv_path = '/workspaces/codespaces-blank/keywords.csv'

# Load keywords from CSV file
def load_keywords(csv_path):
    if not os.path.exists(csv_path):
        return []
    
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]

# Create the directory for files with found keywords
os.makedirs(found_keyword_dir, exist_ok=True)

def search_keywords_in_file(filepath, keywords):
    try:
        with open(filepath, 'r') as file:
            content = json.load(file)
            content_str = json.dumps(content)
            for keyword in keywords:
                if keyword in content_str:
                    return True
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return False

def move_file(src, dst):
    try:
        shutil.move(src, dst)
        print(f"Moved {src} to {dst}")
    except Exception as e:
        print(f"Error moving file {src} to {dst}: {e}")

# Load keywords
keywords = load_keywords(keywords_csv_path)

if not os.path.exists(latest_files_dir):
    print(f"The directory {latest_files_dir} does not exist.")
else:
    json_files = [f for f in os.listdir(latest_files_dir) if f.endswith('.json')]
    if not json_files:
        print(f"No JSON files found in the directory {latest_files_dir}.")
    else:
        for filename in json_files:
            filepath = os.path.join(latest_files_dir, filename)
            print(f"Checking file: {filepath}")
            if search_keywords_in_file(filepath, keywords):
                print(f"Keyword found in {filename}")
                move_file(filepath, os.path.join(found_keyword_dir, filename))
            else:
                print(f"No keywords found in {filename}")

        # Delete all files from the latest_files directory
        for filename in os.listdir(latest_files_dir):
            file_path = os.path.join(latest_files_dir, filename)
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

print("Process completed.")
