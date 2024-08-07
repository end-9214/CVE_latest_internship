import streamlit as st
import os
import json
import re

# Directory containing the JSON files with keywords
found_keyword_dir = '/workspaces/codespaces-blank/Found_Keyword_files'

# Keywords to search for (these can be made dynamic or user-defined)
keywords = ['airflow', 'SamsungMobile', 'hackerone']

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
    # Find all occurrences of "baseScore" and extract their values
    matches = re.findall(r'"baseScore":\s*(\d+(\.\d+)?)', content_str)
    if matches:
        # Convert the first match to float
        base_score = float(matches[0][0])
        return base_score
    return 0.0  # Default baseScore if not found

# Function to filter files by keyword and extract baseScore
def filter_files_by_keyword(files_content, keyword):
    filtered_files = {}
    for filename, content in files_content.items():
        content_str = json.dumps(content)
        if keyword in content_str:
            # Extract baseScore from the JSON content string
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

# Load JSON files from the directory
files_content = load_json_files(found_keyword_dir)

# Streamlit UI
st.title("CVE JSON Files Viewer")

# Initialize session state to track which keyword and file details are shown
if 'visible_keyword' not in st.session_state:
    st.session_state.visible_keyword = None
if 'visible_file' not in st.session_state:
    st.session_state.visible_file = None

# Display list of keywords
st.write("### List of Keywords:")
for keyword in keywords:
    if st.button(keyword):
        if st.session_state.visible_keyword == keyword:
            st.session_state.visible_keyword = None
        else:
            st.session_state.visible_keyword = keyword

# Filter files based on selected keyword
if st.session_state.visible_keyword:
    filtered_files = filter_files_by_keyword(files_content, st.session_state.visible_keyword)

    # Sort files by baseScore in descending order
    sorted_files = sorted(filtered_files.items(), key=lambda x: x[1]['baseScore'], reverse=True)

    # Display list of files as buttons
    if sorted_files:
        st.write("### List of files with baseScore:")
        for filename, details in sorted_files:
            button_label = f"{filename} (Base Score: {details['baseScore']:.1f})"
            if st.button(button_label):
                if st.session_state.visible_file == filename:
                    st.session_state.visible_file = None
                else:
                    st.session_state.visible_file = filename

            # Display details if this file is the visible one
            if st.session_state.visible_file == filename:
                selected_file_content = details['content']
                file_details = extract_details(selected_file_content)
                
                st.write(f"**CVE ID**: {file_details['CVE ID']}")
                st.write(f"**Assigner**: {file_details['Assigner']}")
                st.write("**Descriptions**:")
                for desc in file_details['Descriptions']:
                    st.write(f"- {desc}")
                
                st.write("**Metrics**:")
                st.json(file_details['Metrics'])
                
                st.write("**References**:")
                for ref in file_details['References']:
                    st.write(f"- {ref.get('url', 'N/A')}")
    else:
        st.write("No files found with the selected keyword.")
