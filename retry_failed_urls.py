import json
import os
import time
import re
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Constants
CONFIG_FILE = "config.yml"
FAILED_URLS_FILE = "failed_urls.txt"
FAILED_URLS_FILE_2 = "failed_urls2.txt"
OUTPUT_FILE = "followers.txt"

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("retry_failed_urls")

def load_config():
    """Load configuration from YAML file."""
    import yaml
    try:
        with open(CONFIG_FILE, "r") as file:
            config = yaml.safe_load(file)
            logger.info(f"Loaded configuration for account: @{config['x_credentials'].get('account_name', 'N/A')}")
            return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise

def setup_driver(headless=True):
    """Set up and return a configured webdriver with the same options as main.py."""
    logger.info(f"Setting up Chrome driver (headless={headless})")
    options = webdriver.ChromeOptions()

    if headless:
        # Options to avoid "DevToolsActivePort file doesn't exist" error
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
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    try:
        driver = webdriver.Chrome(options=options)
        logger.info("Chrome driver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome driver: {e}")
        raise

def login_to_x(driver, username, password):
    """Log in to the X account."""
    logger.info(f"Attempting to log in as @{username}")
    driver.get("https://x.com/login")
    try:
        # Wait for login form
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']"))
        )
        username_input.send_keys(username)
        username_input.send_keys("\n")

        # Handle potential display name verification
        try:
            verify_username = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@data-testid='ocfEnterTextTextInput']"))
            )
            verify_username.send_keys(username)
            verify_username.send_keys("\n")
        except TimeoutException:
            pass  # No verification needed

        # Enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='current-password']"))
        )
        password_input.send_keys(password)
        password_input.send_keys("\n")

        # Wait for login confirmation
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']"))
        )
        logger.info("Successfully logged in to X.")
        return True
    except Exception as e:
        logger.error(f"Failed to log in: {e}")
        return False

def get_username_from_url(driver, url):
    """Visit URL and extract username from final destination."""
    logger.info(f"Processing URL: {url}")
    try:
        driver.get(url)
        time.sleep(3)  # Wait for redirects to complete

        final_url = driver.current_url
        logger.info(f"Final URL: {final_url}")

        # Extract username from URL
        username = None
        # Pattern 1: screen_name in query params
        screen_name_match = re.search(r"screen_name=([^&]+)", final_url)
        if screen_name_match:
            username = screen_name_match.group(1)
        # Pattern 2: URL path
        else:
            path_match = re.search(r"x\.com/([^/\?]+)", final_url)
            if path_match and path_match.group(1) not in ["intent", "i", "user"]:
                username = path_match.group(1)

        return username
    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        return None

def append_to_file(file_path, content):
    """Append content to a file, ensuring it exists."""
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content + "\n")

def main():
    logger.info("Starting retry_failed_urls.py...")
    config = load_config()
    username = config["x_credentials"]["username"]
    password = config["x_credentials"]["password"]

    # Set up the browser driver
    driver = setup_driver()
    try:
        # Log in to X
        if not login_to_x(driver, username, password):
            logger.error("Login failed. Exiting script.")
            return

        # Read failed URLs
        if not os.path.exists(FAILED_URLS_FILE):
            logger.error(f"{FAILED_URLS_FILE} not found. Exiting script.")
            return

        with open(FAILED_URLS_FILE, "r", encoding="utf-8") as infile:
            failed_urls = [line.strip() for line in infile if line.strip()]

        for url in failed_urls:
            username = get_username_from_url(driver, url)
            if username:
                logger.info(f"Extracted username: {username}")
                append_to_file(OUTPUT_FILE, username)
            else:
                logger.warning(f"Failed to extract username from URL: {url}")
                append_to_file(FAILED_URLS_FILE_2, url)

    finally:
        driver.quit()
        logger.info("Script completed. Browser closed.")

if __name__ == "__main__":
    main()