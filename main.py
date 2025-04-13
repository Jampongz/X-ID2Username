import json
import re
import os
import time
import logging
import yaml
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Constants
CONFIG_FILE = "config.yml"
OUTPUT_FILE = "followers.txt"
FAILED_URLS_FILE = "failed_urls.txt"
LOG_FILE = f"follower_extractor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
UPDATE_FREQUENCY = 1  # Write to file after every X successful username extractions

# Set up logging
def setup_logging():
    """Configure logging to both file and console"""
    logger = logging.getLogger('follower_extractor')
    logger.setLevel(logging.INFO)
    
    # Create file handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def load_config():
    """Load configuration from YAML file"""
    logger.info(f"Loading configuration from {CONFIG_FILE}")
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = yaml.safe_load(file)
            logger.info(f"Configuration loaded for account: @{config['x_credentials'].get('account_name', 'N/A')}")
            return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def setup_driver(headless=True):
    """Set up and return a configured webdriver"""
    logger.info(f"Setting up Chrome driver (headless={headless})")
    options = webdriver.ChromeOptions()
    
    if headless:
        # Fix for "DevToolsActivePort file doesn't exist" error
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
    
    # Common options for both headless and non-headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=options)
        logger.info("Chrome driver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome driver: {e}")
        
        # Fallback to non-headless if headless fails
        if headless:
            logger.info("Trying to initialize Chrome in non-headless mode as fallback")
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-notifications")
            options.add_argument("--start-maximized")
            driver = webdriver.Chrome(options=options)
            logger.info("Chrome driver initialized in non-headless mode")
            return driver
        else:
            raise

def login_to_x(driver, username, password):
    """Login to X account"""
    logger.info(f"Attempting to login as @{username}")
    driver.get("https://x.com/login")
    
    try:
        # Wait for login form
        logger.info("Waiting for login form...")
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']"))
        )
        username_input.send_keys(username)
        username_input.send_keys(Keys.RETURN)
        logger.info("Username submitted")
        
        # Check if we need to enter display name instead of just username
        try:
            logger.info("Checking for additional username verification...")
            verify_username = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@data-testid='ocfEnterTextTextInput']"))
            )
            verify_username.send_keys(username)
            verify_username.send_keys(Keys.RETURN)
            logger.info("Additional username verification completed")
        except TimeoutException:
            # No verification needed, continue
            logger.info("No additional username verification required")
            pass
        
        # Enter password
        logger.info("Entering password...")
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='current-password']"))
        )
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        
        # Wait for successful login (home timeline)
        logger.info("Waiting for home timeline to confirm login...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']"))
        )
        logger.info("🔓 LOGIN SUCCESSFUL: Successfully logged in to X")
        return True
        
    except Exception as e:
        logger.error(f"⚠️ LOGIN FAILED: {e}")
        try:
            screenshot_file = f"login_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_file)
            logger.info(f"Screenshot saved as {screenshot_file}")
        except:
            logger.error("Failed to save screenshot")
        return False

def extract_urls_from_follower_json(file_path):
    """Extract user links from the follower.json file"""
    logger.info(f"Reading follower.json file from {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Load directly as JSON since it's a .json file
            try:
                json_data = json.load(file)
                logger.info("JSON data loaded successfully")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                # If direct JSON parsing fails, try to extract JSON portion (fallback)
                content = file.read()
                json_match = re.search(r'(\[.*?\])', content, re.DOTALL)
                if not json_match:
                    raise ValueError("Could not find valid JSON data in the file")
                json_data = json.loads(json_match.group(1))
            
            # Extract all user links
            user_links = [item["follower"]["userLink"] for item in json_data if "follower" in item and "userLink" in item["follower"]]
            logger.info(f"Found {len(user_links)} user links in follower.json")
            return user_links
    except Exception as e:
        logger.error(f"Error processing follower.json: {e}")
        raise

def get_username_from_url(driver, url):
    """Visit URL and extract username from final destination"""
    logger.info(f"Processing URL: {url}")
    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for redirects to complete
        logger.info("Waiting for redirects to complete...")
        time.sleep(3)
        
        # Check for any additional redirects
        current_url = driver.current_url
        start_time = time.time()
        max_wait = 10  # Maximum time to wait for redirects
        
        while time.time() - start_time < max_wait:
            # Check if URL has changed after a short wait
            time.sleep(1)
            if driver.current_url != current_url:
                current_url = driver.current_url
                logger.info(f"Redirect detected to: {current_url}")
            else:
                # URL stabilized
                break
        
        final_url = driver.current_url
        logger.info(f"Final URL: {final_url}")
        
        # Extract username from the URL
        username = None
        
        # Pattern 1: ?screen_name=USERNAME
        screen_name_match = re.search(r'screen_name=([^&]+)', final_url)
        if screen_name_match:
            username = screen_name_match.group(1)
            logger.info(f"Found username from screen_name parameter: {username}")
            return username
        
        # Pattern 2: x.com/USERNAME (but not system paths)
        path_match = re.search(r'x\.com/([^/\?]+)', final_url)
        if path_match and path_match.group(1) not in ["intent", "i", "user"]:
            username = path_match.group(1)
            logger.info(f"Found username from URL path: {username}")
            return username
        
        # Pattern 3: Try to extract from page content
        try:
            # Wait for page elements to load
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Multiple methods to try finding the username in the page
            # Method 1: Look for username in the title
            title = driver.title
            if '@' in title:
                username_match = re.search(r'@(\w+)', title)
                if username_match:
                    username = username_match.group(1)
                    logger.info(f"Found username in page title: {username}")
                    return username
            
            # Method 2: Look for username in meta tags
            username_meta = driver.execute_script("""
                var metas = document.getElementsByTagName('meta');
                for (var i = 0; i < metas.length; i++) {
                    if (metas[i].getAttribute('content') && metas[i].getAttribute('content').includes('@')) {
                        return metas[i].getAttribute('content');
                    }
                }
                return null;
            """)
            
            if username_meta:
                username_match = re.search(r'@(\w+)', username_meta)
                if username_match:
                    username = username_match.group(1)
                    logger.info(f"Found username in meta tag: {username}")
                    return username
            
            # Method 3: Look for verified username elements
            username_element = driver.execute_script("""
                // Look for username in any element with @ symbol
                var elements = document.querySelectorAll('div, span, a');
                for (var i = 0; i < elements.length; i++) {
                    if (elements[i].textContent && elements[i].textContent.includes('@')) {
                        return elements[i].textContent;
                    }
                }
                return null;
            """)
            
            if username_element:
                username_match = re.search(r'@(\w+)', username_element)
                if username_match:
                    username = username_match.group(1)
                    logger.info(f"Found username in page element: {username}")
                    return username
            
        except Exception as e:
            logger.warning(f"Error extracting username from page content: {e}")
        
        # If still no username found, save the URL for manual inspection
        if not username:
            logger.warning(f"Could not extract username from URL: {final_url}")
            return None
            
    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        return None

def append_to_file(file_path, line):
    """Append a single line to a file with error handling"""
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{line}\n")
        return True
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        return False

def main():
    # Initialize logger
    global logger
    logger = setup_logging()
    logger.info("============ FOLLOWER EXTRACTOR STARTED ============")
    
    try:
        # Load configuration for login
        config = load_config()
        username = config['x_credentials']['username']
        password = config['x_credentials']['password']
        
        # Path to follower.json file
        follower_json_path = "follower.json"
        
        # Extract URLs from follower.json
        user_links = extract_urls_from_follower_json(follower_json_path)
        
        # Setup browser - can use non-headless for debugging
        headless = True
        driver = setup_driver(headless=headless)
        
        # Clear output files before starting (to avoid appending to existing files)
        open(OUTPUT_FILE, "w").close()
        open(FAILED_URLS_FILE, "w").close()
        
        try:
            # First, login to X/Twitter
            if not login_to_x(driver, username, password):
                logger.error("Failed to login to X/Twitter. Aborting.")
                return
            
            # Process each URL and extract usernames
            successful_count = 0
            failed_count = 0
            
            for i, url in enumerate(user_links):
                logger.info(f"Processing URL {i+1}/{len(user_links)}")
                
                username = get_username_from_url(driver, url)
                
                if username:
                    # Write username to file immediately
                    append_to_file(OUTPUT_FILE, username)
                    successful_count += 1
                    logger.info(f"Found and saved username: {username} ({successful_count} total)")
                else:
                    # Write failed URL to file immediately
                    append_to_file(FAILED_URLS_FILE, url)
                    failed_count += 1
                    logger.warning(f"Failed to extract username from URL: {url} ({failed_count} total)")
                
                # Sleep between requests to avoid rate limiting
                if i < len(user_links) - 1:  # Don't wait after the last one
                    wait_time = 2  # Seconds between requests
                    logger.info(f"Waiting {wait_time} seconds before next request...")
                    time.sleep(wait_time)
            
            logger.info(f"✅ EXTRACTION COMPLETE: Found {successful_count} usernames out of {len(user_links)} links")
            logger.info(f"Results saved to {OUTPUT_FILE}")
            
            if failed_count > 0:
                logger.info(f"Failed URLs saved to {FAILED_URLS_FILE}")
        
        finally:
            # Always close the driver
            logger.info("Closing browser...")
            driver.quit()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    
    logger.info("============ FOLLOWER EXTRACTOR FINISHED ============")

if __name__ == "__main__":
    main()
