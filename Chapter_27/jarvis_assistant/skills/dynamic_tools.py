# CODE LOCATION: jarvis-assistant/skills/dynamic_tools.py

import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration & Archive Setup ---
ARCHIVE_DIR = Path(__file__).parent.parent / "data" / "scraped_data"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def download_media(url, folder, filename):
    """
    The Archivist: Takes a URL and saves the raw binary data as an image file.
    """
    try:
        # Clean the filename to remove characters that Windows/Linux don't like
        safe_name = "".join(x for x in filename if x.isalnum() or x in "._- ").strip()
        save_path = folder / f"{safe_name}.jpg"

        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return str(save_path)
    except Exception as e:
        print(f"[DownloadError] Could not save {filename}: {e}")
    return None

def scrape_dynamic_site(url, selector):
    """
    The Operator: Launches a headless browser, scrolls to load content, 
    and captures text, links, and images.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print(f"[DynamicTool] Visiting: {url}")
        driver.get(url)

        # Wait for scripts and simulate a human scroll to trigger 'Lazy Loading'
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 500);")
        print("[DynamicTool] Simulating scroll to trigger image loading...")
        time.sleep(1)
        
        # Capture a screenshot for debugging
        screenshot_path = ARCHIVE_DIR / "debug_view.png"
        driver.save_screenshot(str(screenshot_path))

        # The 'Waiting Game'
        wait = WebDriverWait(driver, 15)
        found_elements = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
        )

        results = []
        print(f"[DynamicTool] Found {len(found_elements)} potential items. Processing...")

        for el in found_elements:
            text = el.text.strip()
            if text:
                href = el.get_attribute('href')
                
                # Image Extraction Logic
                src = None
                try:
                    if el.tag_name == 'img':
                        src = el.get_attribute('src')
                    else:
                        img = el.find_element(By.TAG_NAME, 'img')
                        src = img.get_attribute('src')
                except:
                    src = None # No image found for this specific element
                
                # --- NEW: THE AUTO-DOWNLOADER ---
                local_image_path = None
                if src and src.startswith("http"):
                    local_image_path = download_media(src, ARCHIVE_DIR, text)
                
                results.append({
                    'text': text,
                    'link': href,
                    'image_url': src,
                    'local_path': local_image_path
                })
        
        # SUCCESS: Return the full list after the loop finishes
        return results

    except TimeoutException:
        print(f"[DynamicTool] TIMEOUT: Element '{selector}' not found. Check debug_view.png!")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    # Test on Marvel Characters
    test_url = "https://www.marvel.com/characters"
    test_selector = "a.ExploreCard__Link" 
    
    print("--- STARTING DYNAMIC TEST ---")
    data = scrape_dynamic_site(test_url, test_selector)
    
    # Print the first 10 results to verify
    for i, item in enumerate(data[:10], 1):
        print(f"\n{i}. {item['text']}")
        print(f"   Link: {item['link']}")
        if item['local_path']:
            print(f"   Image Saved To: {item['local_path']}")
        else:
            print("   Image: Not available")