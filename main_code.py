import requests
import os
import json
import re
from datetime import datetime, timedelta

# Define repository details
owner = 'CVEProject'
repo = 'cvelistV5'
token = os.getenv('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')  # Use environment variable for GitHub token

# Directory to save files
local_directory = 'latest_files'
os.makedirs(local_directory, exist_ok=True)

# Define time window (1 hour ago)
time_window = datetime.utcnow() - timedelta(hours=1)

# GitHub API URL for commits
commits_url = f'https://api.github.com/repos/{owner}/{repo}/commits'

# Headers for authentication
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Get commits from the last hour
response = requests.get(commits_url, headers=headers)
response.raise_for_status()  # Ensure the request was successful
commits = response.json()

# Function to extract baseScore from JSON content by searching for "baseScore"
def extract_base_score(content_str):
    matches = re.findall(r'"baseScore":\s*(\d+(\.\d+)?)', content_str)
    if matches:
        return float(matches[0][0])
    return 0.0  # Default baseScore if not found

# Download the latest files
for commit in commits:
    commit_time = datetime.strptime(commit['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
    
    if commit_time > time_window:
        commit_url = commit['url']
        commit_response = requests.get(commit_url, headers=headers)
        commit_response.raise_for_status()  # Ensure the request was successful
        commit_data = commit_response.json()
        
        for file in commit_data.get('files', []):
            filename = file['filename']
            
            if filename.startswith('cves/2024/') and filename.endswith('.json') and os.path.basename(filename).startswith('CVE-2024-'):
                file_url = f'https://raw.githubusercontent.com/{owner}/{repo}/main/{filename}'
                file_response = requests.get(file_url)
                
                if file_response.status_code == 200:
                    local_path = os.path.join(local_directory, os.path.basename(filename))
                    with open(local_path, 'wb') as local_file:
                        local_file.write(file_response.content)
                    print(f"Downloaded and saved: {filename}")
                else:
                    print(f"Failed to download {filename}, status code: {file_response.status_code}")

# Function to load JSON files
def load_json_files(directory):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    files_content = {}
    for filename in json_files:
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as file:
            content = json.load(file)
            files_content[filename] = content
    return files_content

# Function to filter files by keyword and extract baseScore
def filter_files_by_keyword(files_content, keyword):
    filtered_files = {}
    for filename, content in files_content.items():
        content_str = json.dumps(content)
        if keyword in content_str:
            base_score = extract_base_score(content_str)
            filtered_files[filename] = {
                "content": content,
                "baseScore": base_score
            }
    return filtered_files

# Keywords to search for (these can be made dynamic or user-defined)
keywords = ['airflow', 'SamsungMobile', 'hackerone']

# Load JSON files from the directory
files_content = load_json_files(local_directory)

# Process each keyword and delete files that do not contain the keyword
for keyword in keywords:
    filtered_files = filter_files_by_keyword(files_content, keyword)
    
    # Handle filtered files (e.g., display them in a web interface)
    if filtered_files:
        print(f"Files with keyword '{keyword}':")
        for filename, details in filtered_files.items():
            print(f"- {filename} (Base Score: {details['baseScore']:.1f})")
    else:
        print(f"No files found with the keyword '{keyword}'.")

# Delete files that do not contain any of the keywords
files_to_keep = set()
for keyword in keywords:
    filtered_files = filter_files_by_keyword(files_content, keyword)
    files_to_keep.update(filtered_files.keys())

# Remove files that are not in the list of files to keep
for filename in os.listdir(local_directory):
    if filename not in files_to_keep:
        file_path = os.path.join(local_directory, filename)
        os.remove(file_path)
        print(f"Deleted extra file: {filename}")

print("Process completed.")
