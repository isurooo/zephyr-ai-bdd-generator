# src/zephyr_writer.py

import os
import requests
import json
import re
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# --- Configuration ---
ZEPHYR_BASE_URL = os.getenv("ZEPHYR_BASE_URL", "https://api.zephyrscale.smartbear.com/v2")
ZEPHYR_API_KEY = os.getenv("ZEPHYR_API_KEY")
ZEPHYR_PROJECT_KEY = os.getenv("ZEPHYR_PROJECT_KEY")
HEADERS = {
    "Authorization": f"Bearer {ZEPHYR_API_KEY}",
    "Content-Type": "application/json"
}

# --- Internal Helper Functions for Folder Management ---

def _get_folders():
    """Fetches top-level folders from Zephyr Scale."""
    url = f"{ZEPHYR_BASE_URL}/folders"
    params = {"projectKey": ZEPHYR_PROJECT_KEY, "maxResults": 200}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json().get('values', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching folders: {e}")
        return []

def _create_zephyr_folder(folder_name: str) -> int | None:
    """Creates a new folder in Zephyr Scale and returns its ID."""
    print(f"Attempting to create new folder: '{folder_name}'...")
    url = f"{ZEPHYR_BASE_URL}/folders"
    payload = {
        "projectKey": ZEPHYR_PROJECT_KEY,
        "name": folder_name,
        "folderType": "TEST_CASE"
    }
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        new_folder = response.json()
        folder_id = new_folder.get('id')
        print(f"✅ Successfully created folder with ID: {folder_id}")
        return folder_id
    except requests.exceptions.RequestException as e:
        print(f"Error creating folder: {e}")
        return None

def _handle_folder_selection():
    """Interactively prompts the user to select or create a folder."""
    while True:
        folders = _get_folders()
        if not folders:
            print("No top-level folders found.")
        else:
            print("\nAvailable Folders:")
            for i, folder in enumerate(folders):
                print(f"  {i + 1}: {folder['name']} (ID: {folder['id']})")
        
        print("\nFolder Options:")
        print("  Enter a number to select an existing folder.")
        print("  Type 'new' to create a new top-level folder.")
        print("  Type 'skip' to create the test case at the root level.")
        
        choice = input("Your choice: ").strip().lower()

        if choice.isdigit() and 1 <= int(choice) <= len(folders):
            return folders[int(choice) - 1]['id']
        elif choice == 'new':
            new_folder_name = input("Enter the name for the new folder: ").strip()
            if new_folder_name:
                return _create_zephyr_folder(new_folder_name)
        elif choice == 'skip':
            return None
        else:
            print("Invalid choice. Please try again.")

def _extract_gwt_from_gherkin(full_gherkin_text: str) -> str:
    """Extracts only the Given, When, Then, And lines from a full Gherkin string."""
    gwt_lines = []
    step_pattern = re.compile(r"^\s*(Given|When|Then|And)\s*(.*)", re.IGNORECASE)
    for line in full_gherkin_text.splitlines():
        stripped_line = line.strip()
        if step_pattern.match(stripped_line):
            gwt_lines.append(stripped_line)
    return "\n".join(gwt_lines)

# --- Main Helper Function ---

def create_zephyr_bdd_test_case(gherkin_content: str, prd_title: str, objective: str = "") -> dict | None:
    """Creates a BDD test case in Zephyr Scale, prompting for folder placement."""
    # 1. Let the user select or create a folder
    print("--- Folder Selection ---")
    folder_id = _handle_folder_selection()
    
    # 2. Create the Test Case
    create_test_case_endpoint = f"{ZEPHYR_BASE_URL}/testcases"
    test_case_name = f"{prd_title} - {datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    create_payload = {
        "name": test_case_name,
        "projectKey": ZEPHYR_PROJECT_KEY,
        "testCaseType": "BDD",
        "objective": objective,
    }

    if folder_id:
        create_payload["folderId"] = folder_id
    else:
        print("ℹ️ No folder selected. Creating test case at the root level.")

    print(f"\nSending test case creation request payload: {json.dumps(create_payload, indent=2)}")

    try:
        response = requests.post(create_test_case_endpoint, headers=HEADERS, json=create_payload)
        response.raise_for_status()
        created_test_case = response.json()
        test_case_key = created_test_case.get('key')
        
        print(f"✅ Successfully created initial test case: Key={test_case_key}")

        # 3. Add the BDD script content
        add_script_endpoint = f"{ZEPHYR_BASE_URL}/testcases/{test_case_key}/testscript"
        gwt_script_text = _extract_gwt_from_gherkin(gherkin_content)

        if not gwt_script_text.strip():
            print("⚠️ Warning: No GWT steps extracted. Skipping script update.")
            return created_test_case

        script_payload = {"type": "bdd", "text": gwt_script_text}
        
        print(f"Attempting to add test script for {test_case_key}...")
        script_response = requests.post(add_script_endpoint, headers=HEADERS, json=script_payload)
        script_response.raise_for_status()
        
        print(f"✅ Successfully added test script for {test_case_key}.")
        return created_test_case

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}\nResponse: {http_err.response.text}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")
        return None
