# CODE LOCATION: jarvis-assistant/skills/web_tools.py

import urllib.robotparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path

# --- Configuration ---
# The User-Agent is essential for ethical, identifiable scraping
USER_AGENT = "JarvisAssistantScraper/1.0 (Ethical Scraping)"
DEFAULT_TIMEOUT = 10
# ---

def check_robots_txt(url):
    """
    Ø Step 1: The Ethical Gatekeeper.
    Checks if the given URL is allowed for our user agent and returns the crawl delay.
    Returns: (bool, int) -> (is_allowed, crawl_delay_seconds)
    """
    try:
        # Determine the base URL for robots.txt (e.g., https://example.com)
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_txt_url = f"{base_url}/robots.txt"
        
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(robots_txt_url)
        # Attempt to read the robots.txt file
        parser.read() 
        
        is_allowed = parser.can_fetch(USER_AGENT, url)
        
        # NOTE: get_crawl_delay() is not standard/reliable, but we can implement basic logic.
        # Returning 0 for now, as planned.
        crawl_delay = 0 
        
        if not is_allowed:
            print(f"[WebTool] Scraping denied for {USER_AGENT} by robots.txt policy at {robots_txt_url}")
            return False, 0
        
        return True, crawl_delay

    except Exception as e:
        print(f"[WebTool] Error checking robots.txt for {url}: {e}. Proceeding with caution.")
        # If we can't read robots.txt, we default to allowing but warn the user.
        return True, 0

def fetch_html(url):
    """
    Ø Step 2: The Network Retrieval.
    Executes the HTTP GET request to retrieve the raw HTML content.
    """
    headers = {'User-Agent': USER_AGENT}
    try:
        # Use a timeout to prevent endless hangs
        response = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
        # Raise an exception for bad status codes (4xx or 5xx errors)
        response.raise_for_status() 
        
        # Check if the content is likely HTML (optional, but good practice)
        if 'text/html' not in response.headers.get('Content-Type', ''):
            print(f"[WebTool] Warning: URL returned non-HTML content type: {response.headers.get('Content-Type')}")
            return None
            
        return response.text
        
    except requests.RequestException as e:
        print(f"[WebTool] Fetch error for {url}: {e}")
        return None

def parse_data(html_content, selector):
    """
    Ø Step 3: The Data Architect.
    Uses a parser to surgically extract specific data based on a CSS selector.
    
    Returns: A list of clean text strings extracted from matching elements, 
             or an empty list on failure.
    """
    if not html_content:
        return []
        
    try:
        # Use the 'lxml' parser for speed and robustness
        # NOTE: Requires 'pip install lxml'
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Use the provided CSS selector to find all matching elements
        tag_results = soup.select(selector)
        
        # *** TWEAK: Extract clean text content from the tags ***
        # This transforms the messy BeautifulSoup object list into a clean string list.
        text_results = [tag.text.strip() for tag in tag_results]
        
        print(f"[WebTool] Extracted {len(text_results)} elements using selector: '{selector}'")
        return text_results
        
    except Exception as e:
        print(f"[WebTool] Parsing error with selector '{selector}': {e}")
        return []

# --- Orchestrator for main.py (Optional but useful helper) ---
def scrape_url_for_selector(url, selector):
    """
    Combines all three steps (Robots -> Fetch -> Parse).
    
    Returns: A list of extracted text strings, or None if the process fails 
             (denied by robots.txt, fetch error, or no content).
    """
    # 1. Ethical Check
    is_allowed, _ = check_robots_txt(url)
    if not is_allowed:
        return None 
        
    # 2. Fetch HTML
    html_content = fetch_html(url)
    if not html_content:
        return None
        
    # 3. Parse Data
    return parse_data(html_content, selector)


if __name__ == '__main__':
    # Simple test case (will only run if this file is executed directly)
    TEST_URL = "https://www.python.org/"
    # Target the main headline of the news/events section
    TEST_SELECTOR = "h2.widget-title" 
    print(f"--- Running Web Tools Test on {TEST_URL} ---")
    
    elements = scrape_url_for_selector(TEST_URL, TEST_SELECTOR)
    
    if elements:
        print("\n--- Successful Scraping Results (First 5) ---")
        for i, el in enumerate(elements[:5]):
            print(f"{i+1}. Content: {el}")
    else:
        print("--- Scraping Test Failed ---")