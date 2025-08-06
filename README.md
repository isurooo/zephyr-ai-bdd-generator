# Zephyr AI

*Instantly convert product requirements into BDD test cases, directly in Zephyr.*

Zephyr AI is a command-line automation tool that bridges the gap between product documentation and QA testing. It uses a powerful AI model to analyze Product Requirement Documents (PRDs) from Confluence, automatically generates comprehensive BDD test cases, and creates them in your Zephyr Scale project, neatly organized into folders.

## What it Does

* **Analyzes PRDs:** Connects securely to Confluence to fetch and process PRD content directly from a page.

* **Generates BDD Test Cases:** Uses Google's Gemini AI to generate comprehensive BDD scenarios in Gherkin syntax, including happy paths, negative scenarios, and edge cases.

* **Automates Zephyr Creation:** Creates BDD test cases in Zephyr Scale and populates them with the AI-generated Gherkin script.

* **Organizes Test Cases:** Allows you to interactively select an existing folder or create a new one within Zephyr to keep your test repository clean.

* **Provides a Robust CLI:** Offers a user-friendly command-line interface with real-time feedback and error diagnostics.

## Tech Stack

* **Language:** Python

* **APIs:** Google Gemini API, Confluence API, Zephyr Scale REST API

* **Key Libraries:** `requests`, `BeautifulSoup`, `google-generativeai`, `python-dotenv`, `atlassian-python-api`

## Setup and Installation

**1. Clone the Repository**

```bash
git clone [https://github.com/YOUR_USERNAME/zephyr-ai-bdd-generator.git](https://github.com/YOUR_USERNAME/zephyr-ai-bdd-generator.git)
cd zephyr-ai-bdd-generator
```

**2. Create and Activate a Virtual Environment**

* **macOS/Linux:**

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

* **Windows:**

  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

**3. Install Dependencies**

```bash
pip install -r requirements.txt
```

**4. Create the Configuration File**
Create a file named `.env` in the root directory of the project. This file will store all your secret keys and configuration variables.

## Configuration (`.env` file)

Copy the following content into your `.env` file and replace the placeholder values with your actual credentials.

```env
# --- Confluence API Credentials ---
# Your organization's Confluence URL (e.g., [https://your-company.atlassian.net](https://your-company.atlassian.net))
CONFLUENCE_URL="YOUR_CONFLUENCE_URL"
# The email address you use to log in to Confluence/Jira
CONFLUENCE_USERNAME="YOUR_CONFLUENCE_EMAIL"
# Your Atlassian API Token ([https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/))
CONFLUENCE_API_TOKEN="YOUR_ATLASSIAN_API_TOKEN"

# --- Gemini AI API Key ---
# Your API key from Google AI Studio ([https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey))
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# --- Zephyr Scale API Credentials ---
# The base URL is always the same for Zephyr Scale Cloud
ZEPHYR_BASE_URL="[https://api.zephyrscale.smartbear.com/v2](https://api.zephyrscale.smartbear.com/v2)"
# Your Zephyr Scale API Token ([https://support.smartbear.com/zephyr-scale-cloud/docs/rest-api/generating-api-access-tokens.html](https://support.smartbear.com/zephyr-scale-cloud/docs/rest-api/generating-api-access-tokens.html))
ZEPHYR_API_KEY="YOUR_ZEPHYR_API_TOKEN"
# The project key for your Zephyr project (e.g., "VX", "PROJ")
ZEPHYR_PROJECT_KEY="YOUR_ZEPHYR_PROJECT_KEY"
```

## How to Run

Execute the main script from the root directory of the project:

```bash
python -m src.main
```

The tool will then guide you through the process:

1.  **Enter PRD Title:** You will be prompted to enter the exact title of the PRD page from Confluence. This title is used to both find the page and as the base name for the test case created in Zephyr.

2.  **Select Zephyr Folder:** After the BDD is generated, the script will display a list of folders from your Zephyr project and ask you to select a destination for the new test case.

## Example PRD Format

For best results, the tool is currently optimized to parse PRDs written in a Gherkin-like format directly within a Confluence page, often inside a code block macro.

**Example PRD on a Confluence Page:**

```gherkin
Given that the Place order window fields are empty by default,
And the user wants to place an order,
Then the user should click on the Select input fields to select desired options,
And enter desired values in Price/Quantity Input fields where applicable.
When user is done filling in all relevant fields,
And all relevant validation checks are completed,
Then the user should see Place Order button enabled
And the user can click on it to place order.
