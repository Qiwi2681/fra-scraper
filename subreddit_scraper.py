import sys
import time
import random

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


def scrape_subreddit(driver, scroll_times: int):
    links_set = set()

    scroll_and_wait(driver, scroll_times)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    post_links = soup.find_all("a")

    for link in post_links:
        href = link.get("href")
        if href and "/comments/" in href:
            links_set.add(href)

    return links_set

# Class for crawling subreddits to get post links


class SubRedditCrawler():
    def __init__(self, scroll_number: int, threads=1):
        self.scroll_number = scroll_number
        self.database = url_database.URLDatabase('seen_posts')
        self.chrome_driver = driver_manager.ParralelDriverManager(threads)

    def scrape(self, subreddit_urls: set) -> set:
        self.database.set_current(subreddit_urls)
        urls = self.database.get_unique()

        if not urls:
            clear = input("Cannot find any unique sub urls, type y to clear cache & retry: ")
            if clear == 'y':
                self.database.clear()
                urls = self.database.get_unique()
            else:
                sys.exit()

        self.chrome_driver.url_pool = list(urls)

        #start tasks
        posts = self.chrome_driver.parallel_url_task(scrape_subreddit, self.scroll_number)

        return posts
