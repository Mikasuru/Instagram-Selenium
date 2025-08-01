import logging
import time
from typing import Iterator

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from config import (BaseUrl, Retires, ScrollPause, WebTimeout)
from exceptions import ScrapingException
from session_manager import load_cookies

class InstagramScraper:
    def __init__(self):
        self.options = uc.ChromeOptions()
        # self.options.add_argument('--headless')
        self.driver = None
        self.wait = None

    def __enter__(self):
        logging.info("Initializing WebDriver...")
        try:
            self.driver = uc.Chrome(options=self.options)
            self.wait = WebDriverWait(self.driver, WebTimeout)
            return self
        except WebDriverException as e:
            raise ScrapingException(f"Failed to initialize Chrome Driver: {e}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            logging.info("Closing WebDriver.")
            self.driver.quit()

    def login(self) -> None:
        if not self.driver:
            raise ScrapingException("Driver not initialized. Use within a 'with' statement.")
        load_cookies(self.driver)

    def GetFollowers(self, username: str, limit: int) -> list[str]:
        logging.info(f"Navigating to {username}'s profile...")
        self.driver.get(f"{BaseUrl}{username}/")

        self.OpenModal(username)
        
        logging.info("Starting to scrape follower list...")
        FollowersSet = self.ScrapeFollowers(limit)

        return list(FollowersSet)[:limit]

    def OpenModal(self, username: str) -> None:
        try:
            FollowersXpath = f"//a[contains(@href, '/{username}/followers/')]"
            FollowersBtn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, FollowersXpath))
            )
            FollowersBtn.click()
            
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            logging.info("Followers modal opened.")
        except TimeoutException:
            raise ScrapingException("Could not find or click the followers button. The profile might be private or does not exist.")

    def ScrapeFollowers(self, limit: int) -> set[str]:
        FollowersSet = set()
        ScrollableXpath = "//div[@role='dialog']//div[contains(@style, 'overflow: hidden auto')]"
        
        try:
            ScrollableDiv = self.wait.until(
                EC.presence_of_element_located((By.XPATH, ScrollableXpath))
            )

            retries = 0
            while len(FollowersSet) < limit:
                CountBefore = len(FollowersSet)
                
                UsrElement = ScrollableDiv.find_elements(By.XPATH, ".//a[@role='link' and .//span]")
                
                if not UsrElement:
                    logging.warning("No user elements found in the scrollable div.")
                    break

                for element in UsrElement:
                    if len(FollowersSet) >= limit:
                        break
                    href = element.get_attribute("href")
                    if href:
                        follower_username = href.strip('/').split('/')[-1]
                        FollowersSet.add(follower_username)

                if len(FollowersSet) >= limit:
                    logging.info(f"Reached the follower limit of {limit}.")
                    break

                # check if end of the list
                if len(FollowersSet) == CountBefore:
                    retries += 1
                    if retries >= Retires:
                        logging.info("Reached the end of the follower list.")
                        break
                    time.sleep(ScrollPause) # wait a few
                else:
                    retries = 0 # reset

                self.driver.execute_script("arguments[0].scrollIntoView(true);", UsrElement[-1])
                time.sleep(ScrollPause)

        except (NoSuchElementException, TimeoutException):
            raise ScrapingException("Could not find the follower list container. Instagram's layout might have changed.")
        
        return FollowersSet