# src/main.py

import os
import datetime
from dotenv import load_dotenv
import google.generativeai as genai

from .confluence_reader import get_prd_content_by_title, clean_confluence_html
from .zephyr_writer import create_zephyr_bdd_test_case

# Load environment variables
load_dotenv()

def generate_bdd_with_gemini(prd_text: str) -> str | None:
    """Generates BDD test cases from PRD text using the Gemini LLM."""
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = f"""You are a meticulous QA Automation Engineer. Your task is to write complete, end-to-end BDD scenarios in Gherkin based on the provided PRD.

**Critical Instructions:**
1.  **No Incomplete Scenarios:** Every `Scenario` must be fully formed.
2.  **Full End-to-End Flow:** Trace the user's journey from `Given` to `Then`.
3.  **Structure and Keywords:** Start with a `Feature` block. Each test case MUST begin with the `Scenario:` keyword. Use `And` instead of `But`.
4.  **Infer Details:** If the PRD is brief, infer logical details needed for a complete test (e.g., user roles, balances, error messages).

Here is the PRD to analyze:
---
{prd_text}
---
"""
    try:
        generation_config = {"temperature": 0.2, "max_output_tokens": 8192}
        response = model.generate_content(prompt, generation_config=generation_config)
        cleaned_text = response.text.replace("```gherkin", "").replace("```", "").strip()
        return cleaned_text
    except Exception as e:
        print(f"Error generating BDD with Gemini: {e}")
        return None

def run_prd_to_bdd_pipeline():
    """The main function to run the PRD-to-BDD pipeline."""
    print("--- Starting Zephyr AI ---")

    # 1. Get PRD details from user
    prd_title = input("Please enter the exact title of the Confluence PRD page: ").strip()
    space_key = input("Please enter the Confluence Space Key (e.g., 'PROJ'): ").strip()

    if not prd_title or not space_key:
        print("PRD Title and Space Key cannot be empty. Aborting.")
        return

    # 2. Retrieve and clean PRD content
    print("\n1. Retrieving PRD content from Confluence...")
    raw_content = get_prd_content_by_title(space_key, prd_title)
    if not raw_content:
        print("Failed to retrieve content. Please check the page title, space key, and your credentials.")
        return

    clean_prd_text = clean_confluence_html(raw_content)
    if not clean_prd_text:
        print("PRD content is empty after cleaning. Aborting.")
        return

    # 3. Generate BDD test cases
    print("2. Generating BDD test cases with Gemini...")
    generated_bdd = generate_bdd_with_gemini(clean_prd_text)

    if generated_bdd:
        print("\n3. Successfully Generated BDD Test Cases ---")
        print(generated_bdd)

        # 4. Create Test Case in Zephyr Scale
        print("\n4. Attempting to create BDD test case(s) in Zephyr Scale...")
        zephyr_test_case_objective = f"Automated BDD test case generated from Confluence PRD '{prd_title}'."
        
        zephyr_response = create_zephyr_bdd_test_case(generated_bdd, prd_title, zephyr_test_case_objective)

        if zephyr_response:
            print("\n✅ Pipeline finished successfully!")
        else:
            print("\n❌ Pipeline finished with errors. Failed to create test case in Zephyr Scale.")
    else:
        print("\n❌ Pipeline finished with errors. BDD generation failed.")

if __name__ == "__main__":
    run_prd_to_bdd_pipeline()
