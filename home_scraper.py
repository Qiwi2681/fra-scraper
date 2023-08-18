import re
import sys

from bs4 import BeautifulSoup

import url_database
import driver_manager

def scrape_subreddits(driver):
    subreddit_set = set()

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
            subreddit_set.add('/r/' + match.group(1))

    return subreddit_set

# Class for crawling home page to get subreddits


class HomePageCrawler():
    def __init__(self, scroll_number: int, threads=1):
        self.scroll_number = scroll_number
        self.threads = threads

        self.database = url_database.URLDatabase('seen_subs')
        self.chrome_driver = driver_manager.ParralelDriverManager(self.threads)


    # scrape more URLs
    def scrape(self) -> set:
        self.chrome_driver.populate_url_pool(['https://reddit.com']*self.threads)

        self.chrome_driver.parallel_url_task(self.chrome_driver.scroll_and_wait, self.scroll_number)

        self.chrome_driver.populate_url_pool(['https://reddit.com']*self.threads)

        current = self.chrome_driver.parallel_url_task(scrape_subreddits)

        print(current)

        self.chrome_driver.stop_drivers()

        self.database.set_current(current)

        subreddits = self.database.get_unique()

        if not subreddits:
            clear = input("Cannot find any unique subreddits, type y to clear cache & retry: ")
            if clear == 'y':
                self.database.clear()
                subreddits = self.database.get_unique()
            else:
                sys.exit()
        return  subreddits
