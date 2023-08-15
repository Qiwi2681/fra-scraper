import re
import time
import random
from concurrent.futures import ThreadPoolExecutor

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

import url_database
import driver_manager


REDDIT_URL = 'https://reddit.com'


def scrape_subreddits(url, driver, scrolls_to_perform):
    subreddit_set = set()

    # Navigate to the current URL of the driver
    driver.get(url)

    # Define a function to scroll down the page and load more results
    def scroll_and_wait(scrolls_to_perform):
        last_height = driver.execute_script(
            "return document.body.scrollHeight")
        scrolls_done = 0
        while scrolls_done < scrolls_to_perform:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            # Adjust the waiting time based on your network speed
            time.sleep(random.randint(200, 300)/100)
            new_height = driver.execute_script(
                "return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls_done += 1

    # Scroll down specified number of times to load more results
    if scrolls_to_perform > 0:
        scroll_and_wait(scrolls_to_perform)
    else:
        wait = WebDriverWait(driver, 10)  # Maximum wait time in seconds
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.font-semibold")))

    # Get the page source after scrolling
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup as before
    soup = BeautifulSoup(page_source, "html.parser")

    # Extract the subreddit names from the href attribute and store them in a set
    a_tags = soup.find_all("a", class_="absolute inset-0")
    for a_tag in a_tags:
        href = a_tag.get("href")
        match = re.search(r'/r/([^/]+)/', href)
        if match:
            subreddit_set.add(match.group(1))

    return subreddit_set

# Class for crawling home page to get subreddits


class HomePageCrawler():
    def __init__(self, scroll_number: int, threads=1):
        self.scroll_number = scroll_number
        self.threads = threads

        self.database = url_database.URLDatabase('seen_subs')
        self.chrome_driver = driver_manager.ParralelDriverManager(threads)

    def get_urls(self) -> set:
        return self.database.update(self.scrape)

    # scrape more URLs
    def scrape(self) -> set:
        unique = set()

        # Start the drivers using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            self.chrome_driver.start_drivers()

            # Submit scrape tasks to the executor
            scrape_tasks = [
                executor.submit(self.scrape_subreddits,
                                self.chrome_driver.drivers[i % self.threads])
                for i in range(self.threads)
            ]

            # Wait for all tasks to complete and gather results
            for task in scrape_tasks:
                scraped_urls = task.result()
                unique.update(scraped_urls)

            # Stop the drivers
            self.chrome_driver.stop_drivers()

        return unique

    def scrape_subreddits(self, driver):
        return scrape_subreddits(REDDIT_URL, driver, self.scroll_number)
