import streamlit as st
import os
import json
import csv
import re

# Directory containing the JSON files with keywords
found_keyword_dir = '/workspaces/codespaces-blank/Found_Keyword_files'
keywords_csv_path = '/workspaces/codespaces-blank/keywords.csv'

# Load keywords from CSV file
def load_keywords(csv_path):
    if not os.path.exists(csv_path):
        return []
    
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        return [row[0] for row in reader]

# Save a new keyword to the CSV file
def save_keyword(keyword, csv_path):
    keywords = load_keywords(csv_path)
    if keyword in keywords:
        st.warning(f"Keyword '{keyword}' already exists!")
    else:
        with open(csv_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([keyword])
        st.success(f"Keyword '{keyword}' added successfully!")

# Delete a keyword from the CSV file
def delete_keyword(keyword, csv_path):
    keywords = load_keywords(csv_path)
    keywords = [k for k in keywords if k != keyword]
    
    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file)
        for k in keywords:
            writer.writerow([k])

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

# Function to extract baseScore from JSON content by searching for "baseScore"
def extract_base_score(content_str):
    matches = re.findall(r'"baseScore":\s*(\d+(\.\d+)?)', content_str)
    if matches:
        base_score = float(matches[0][0])
        return base_score
    return 0.0  # Default baseScore if not found

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

# Function to extract important details from the JSON content
def extract_details(json_content):
    cve_id = json_content.get('cveMetadata', {}).get('cveId', 'N/A')
    assigner = json_content.get('cveMetadata', {}).get('assignerShortName', 'N/A')
    descriptions = [desc.get('value', 'N/A') for desc in json_content.get('containers', {}).get('cna', {}).get('descriptions', [])]
    affected_descriptions = []

    if 'problemTypes' in json_content.get('containers', {}).get('cna', {}):
        affected_descriptions = [
            desc.get('description', 'N/A') for problem in json_content.get('containers', {}).get('cna', {}).get('problemTypes', [])
            for desc in problem.get('descriptions', []) if 'affected' in desc.get('description', '')
        ]
    
    # Correctly extract metrics if available
    metrics = json_content.get('containers', {}).get('cna', {}).get('metrics', [])
    
    references = json_content.get('containers', {}).get('cna', {}).get('references', [])
    
    selected_descriptions = affected_descriptions if affected_descriptions else descriptions

    return {
        "CVE ID": cve_id,
        "Assigner": assigner,
        "Descriptions": selected_descriptions,
        "Metrics": metrics,
        "References": references
    }

# Initialize session state
if 'visible_keyword' not in st.session_state:
    st.session_state.visible_keyword = None

if 'visible_file' not in st.session_state:
    st.session_state.visible_file = None

# Load keywords and JSON files
keywords = load_keywords(keywords_csv_path)
files_content = load_json_files(found_keyword_dir)

# Streamlit UI
st.title("CVE JSON Files Viewer")

# Add new keyword
st.write("### Add a new keyword")
new_keyword = st.text_input("Enter keyword:")
if st.button("Add Keyword"):
    if new_keyword:
        save_keyword(new_keyword, keywords_csv_path)
        st.experimental_rerun()  # Refresh the page after adding a keyword

# Delete an existing keyword
st.write("### Delete an existing keyword")
keyword_to_delete = st.selectbox("Select keyword to delete", options=keywords)
if st.button("Delete Keyword"):
    if keyword_to_delete:
        delete_keyword(keyword_to_delete, keywords_csv_path)
        st.success(f"Keyword '{keyword_to_delete}' deleted successfully!")
        st.experimental_rerun()  # Refresh the page after deleting a keyword

# Display list of keywords
st.write("### List of Keywords:")
for keyword in keywords:
    if st.button(keyword):
        st.session_state.visible_keyword = keyword

# Filter files based on selected keyword
if st.session_state.visible_keyword:
    filtered_files = filter_files_by_keyword(files_content, st.session_state.visible_keyword)

    sorted_files = sorted(filtered_files.items(), key=lambda x: x[1]['baseScore'], reverse=True)

    if sorted_files:
        st.write("### List of files with baseScore:")
        for filename, details in sorted_files:
            button_label = f"{filename} (Base Score: {details['baseScore']:.1f})"
            if st.button(button_label):
                st.session_state.visible_file = filename

            if st.session_state.visible_file == filename:
                selected_file_content = details['content']
                file_details = extract_details(selected_file_content)
                
                st.write(f"**CVE ID**: {file_details['CVE ID']}")
                st.write(f"**Assigner**: {file_details['Assigner']}")
                st.write("**Descriptions**:")
                for desc in file_details['Descriptions']:
                    st.write(f"- {desc}")
                
                st.write("**Metrics**:")
                if file_details['Metrics']:  # Check if metrics is not empty
                    st.json(file_details['Metrics'])
                else:
                    st.write("No metrics available.")
                
                st.write("**References**:")
                for ref in file_details['References']:
                    st.write(f"- {ref.get('url', 'N/A')}")
    else:
        st.write("No files found with the selected keyword.")
