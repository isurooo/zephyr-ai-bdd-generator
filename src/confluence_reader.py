# src/confluence_reader.py

import os
from atlassian import Confluence
from bs4 import BeautifulSoup
import html2text

def get_prd_content_by_title(space_key: str, page_title: str) -> str | None:
    """
    Fetches the raw Confluence Storage Format content of a page by its title.
    """
    try:
        confluence = Confluence(
            url=os.getenv("CONFLUENCE_URL"),
            username=os.getenv("CONFLUENCE_USERNAME"),
            password=os.getenv("CONFLUENCE_API_TOKEN"),
            cloud=True
        )
        page = confluence.get_page_by_title(space=space_key, title=page_title, expand='body.storage')
        if page and 'body' in page and 'storage' in page['body']:
            return page['body']['storage']['value']
        return None
    except Exception as e:
        print(f"Error fetching page by title '{page_title}': {e}")
        return None

def clean_confluence_html(html_content: str) -> str:
    """
    Cleans Confluence HTML by specifically finding and extracting text from known
    macros (like code blocks) and then cleaning the remaining content.
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_texts = []

    # 1. Specifically find all Confluence code blocks.
    for code_block_body in soup.find_all('ac:plain-text-body'):
        block_text = code_block_body.get_text(strip=True)
        if block_text:
            extracted_texts.append(block_text)
        if code_block_body.parent:
            code_block_body.parent.decompose()

    # 2. Process the rest of the HTML.
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.body_width = 0
    remaining_text = h.handle(str(soup))
    
    if remaining_text.strip():
         extracted_texts.append(remaining_text.strip())

    # 3. Join all the text pieces together.
    final_cleaned_text = "\n\n".join(extracted_texts)

    if not final_cleaned_text:
        print("\n❌ CRITICAL WARNING: The cleaning process resulted in an empty PRD.")
    else:
        print("\n--- Cleaned PRD Content for LLM ---")
        print(final_cleaned_text)
        print("---------------------------------\n")

    return final_cleaned_text
