import time
import random

from concurrent.futures import ThreadPoolExecutor
from selenium.common import exceptions as se
from bs4 import BeautifulSoup

import url_database
import driver_manager


def scroll_and_wait(driver, scroll_times):
    last_height = driver.execute_script("return document.body.scrollHeight")
    i = 0
    while i < scroll_times:
        # Check if the "View more comments" button is present
        load_more_button = None
        try:
            load_more_button = driver.find_element(
                "css selector", "button.button-brand")
        except se.NoSuchElementException:
            pass

        if load_more_button:
            # Click the "View more comments" button
            load_more_button.click()
            # Wait for the comments to load
            time.sleep(random.randint(200, 300)/100)

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        # Adjust the waiting time based on your network speed
        time.sleep(random.randint(200, 300)/100)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        i += 1

# Function to scrape post links for a given subreddit


def scrape_subreddit(driver, subs: list, scroll_times: int):
    links_set = set()
    for sub in subs:
        url = f'https://www.reddit.com/r/{sub}/'

        driver.get(url)
        scroll_and_wait(driver, scroll_times)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        post_links = soup.find_all("a")

        for link in post_links:
            href = link.get("href")
            if href and f"/r/{sub}/comments/" in href:
                links_set.add(href)

    return links_set

# Class for crawling subreddits to get post links


class SubRedditCrawler():
    def __init__(self, scroll_number: int, threads=1):
        self.scroll_number = scroll_number
        self.threads = threads
        self.database = url_database.URLDatabase('seen_posts')
        self.chrome_driver = driver_manager.ParralelDriverManager(threads)

    def get_urls(self, subreddit_urls: list) -> set:
        unique = set()

        # Split the list of subreddit URLs into equal chunks based on the number of threads
        url_chunks = self.split_list_into_chunks(subreddit_urls, self.threads)

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            self.chrome_driver.start_drivers()

            # Submit scrape tasks to the executor for each URL chunk
            scrape_tasks = [
                executor.submit(
                    self.scrape_posts, self.chrome_driver.drivers[i % self.threads], url_chunk)
                for i, url_chunk in enumerate(url_chunks)
            ]

            # Wait for all tasks to complete and gather results
            for task in scrape_tasks:
                scraped_urls = task.result()
                unique.update(scraped_urls)

            # Stop the drivers
            self.chrome_driver.stop_drivers()

        return unique

    def split_list_into_chunks(self, lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    def scrape_posts(self, driver, url_chunk):
        return scrape_subreddit(driver, url_chunk, self.scroll_number)
