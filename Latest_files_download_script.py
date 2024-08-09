import requests
import os
from datetime import datetime, timedelta

# Define repository details
owner = 'CVEProject'
repo = 'cvelistV5'
token = 'auth_token'  # Replace with your actual GitHub token

# Define time window (1 hour ago)
time_window = datetime.utcnow() - timedelta(seconds=20)

# GitHub API URL for commits
commits_url = f'https://api.github.com/repos/{owner}/{repo}/commits'

# Headers for authentication
headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Get commits from the last hour
response = requests.get(commits_url, headers=headers)
commits = response.json()

# Directory to save files
os.makedirs('latest_files', exist_ok=True)

# Debugging: Print time window for reference
print(f"Checking commits since {time_window.isoformat()}")

for commit in commits:
    commit_time = datetime.strptime(commit['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
    
    # Debugging: Print commit time for reference
    print(f"Commit time: {commit_time.isoformat()}")
    
    if commit_time > time_window:
        commit_url = commit['url']
        commit_response = requests.get(commit_url, headers=headers)
        commit_data = commit_response.json()
        
        for file in commit_data['files']:
            filename = file['filename']
            
            # Check if the file is within the 'cves/2024/' directory and starts with 'CVE-2024-'
            if filename.startswith('cves/2024/') and filename.endswith('.json') and os.path.basename(filename).startswith('CVE-2024-'):
                # Download the file
                file_url = f'https://raw.githubusercontent.com/{owner}/{repo}/main/{filename}'
                file_response = requests.get(file_url)
                
                if file_response.status_code == 200:
                    # Save the file locally
                    local_path = os.path.join('latest_files', os.path.basename(filename))
                    with open(local_path, 'wb') as local_file:
                        local_file.write(file_response.content)
                    print(f"Downloaded and saved: {filename}")
                else:
                    print(f"Failed to download {filename}, status code: {file_response.status_code}")

print("Process completed.")
