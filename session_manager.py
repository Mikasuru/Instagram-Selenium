import json
import logging
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import SessionFile, BaseUrl, ElementXpath, WebTimeout
from exceptions import SessionNotFoundException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

def create_session() -> None:
    logging.info("Starting new session creation process...")
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    
    try:
        driver.get(BaseUrl)
        logging.info("Please log in to your Instagram account in the browser window.")
        logging.info("The script will automatically detect the login and save the session.")

        wait = WebDriverWait(driver, timeout=300) # 5 min to login
        wait.until(EC.presence_of_element_located((By.XPATH, ElementXpath)))
        
        logging.info("Login successful! Saving session cookies...")
        cookies = driver.get_cookies()
        
        with open(SessionFile, "w") as f:
            json.dump(cookies, f, indent=4)
            
        logging.info(f"Session saved successfully to '{SessionFile}'")
        time.sleep(3)
        
    except TimeoutException:
        logging.error("Login process timed out. Please try running --create-session again.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during session creation: {e}")
    finally:
        driver.quit()

def load_cookies(driver: uc.Chrome) -> None:
    try:
        with open(SessionFile, "r") as f:
            cookies = json.load(f)
        
        driver.get(BaseUrl)
        for cookie in cookies:
            driver.add_cookie(cookie)
        logging.info("Session cookies loaded successfully.")
        driver.refresh()
        
    except FileNotFoundError:
        raise SessionNotFoundException(
            f"Session file '{SessionFile}' not found. "
            "Please run the script with '--create-session' argument first to log in."
        )