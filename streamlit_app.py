import streamlit as st
import requests
import json
import os
from datetime import datetime
import pytz
from streamlit_keycloak import login

# Keycloak configuration
KEYCLOAK_SERVER_URL = 'https://bluiam01.blusapphire.com/'
KEYCLOAK_REALM = 'prod2'
KEYCLOAK_CLIENT_ID = 'streamlit'
REDIRECT_URI = 'http://localhost:8501'  # Streamlit runs on this by default
# Directory containing the JSON playbook files
PLAYBOOKS_DIR = "playbooks/"

# Dictionary to map use case names to their respective JSON files and URLs
PLAYBOOKS = {
    "Phishing": {"file": "static_alerts/phishing.json", "url": "https://oneflow.blusapphire.com/api/v1/workflows/f1d3bba3-a37f-4cff-bf5f-7d4469424cd0/execute"},
    "Malware": {"file": "static_alerts/malware.json", "url": "https://oneflow.blusapphire.com/api/v1/workflows/76064176-de12-415f-ac56-d5744abfcdbf/execute"},
    "Ransomware": {"file": "static_alerts/ransomware.json", "url": "https://oneflow.blusapphire.com/api/v1/workflows/4db7d402-8ebd-4ea9-907b-17eab0afbbb8/execute"},
    "Suspicious User Behaviour": {"file": "static_alerts/suspicious_user_behavior.json", "url": "https://oneflow.blusapphire.com/api/v1/workflows/95ca7158-3c4e-431f-8826-c488b772fd7f/execute"},
    "System Quarantine": {"file": "static_alerts/system_quarantine.json", "url": "https://oneflow.blusapphire.com/api/v1/workflows/8d1b4725-10f3-4c6e-b0ef-0f7761090cbc/execute"},
    "System Release": {"file": "static_alerts/system_release.json", "url": "https://oneflow.blusapphire.com/api/v1/workflows/ae59b574-9d40-48fa-8642-9ad5d284112e/execute"},
}

# Function to update timestamps in JSON data
def update_timestamps(json_data):
    current_time = datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    if 'event' in json_data:
        json_data['event']['created'] = current_time
    if 'alert' in json_data:
        json_data['alert']['created'] = current_time
    return json_data

def main():
    # Display a select box for choosing a use case
    use_case = st.selectbox("Select a Use Case", ["Select a playbook"] + list(PLAYBOOKS.keys()))
    # Show the selected JSON file contents
    if use_case != "Select a playbook":
        playbook_info = PLAYBOOKS[use_case]
        json_file_path = playbook_info["file"]

        try:
            with open(json_file_path, "r") as json_file:
                json_data = json.load(json_file)
                updated_json_data = update_timestamps(json_data)
                st.json(updated_json_data)
            headers = {
                    "Authorization": "Bearer bc5b20bc-8b0c-4351-9fc0-00ae0b0521f1"
                    }
            # Button to send the JSON to the playbook URL
            if st.button(f"Send {use_case} to Playbook"):
                response = requests.post(playbook_info["url"], headers=headers, json=json_data)
                if response.status_code == 200:
                    st.success(f"Successfully sent {use_case} to {playbook_info['url']}")
                else:
                    st.error(f"Failed to send {use_case}. Status code: {response.status_code}")
                    st.write(response.text)
        except FileNotFoundError:
            st.error(f"File not found: {json_file_path}")
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON from file: {json_file_path}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

st.title("Playbook Executor")

keycloak = login(
    url=KEYCLOAK_SERVER_URL,
    realm=KEYCLOAK_REALM,
    client_id=KEYCLOAK_CLIENT_ID,
)

if keycloak.authenticated:
    main()
