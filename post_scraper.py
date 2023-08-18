import re
import sys
import time
import json
import random

from selenium.common import exceptions as se
from bs4 import BeautifulSoup

import driver_manager
import url_database


def scroll_and_wait(driver, max_time=300):
    start_time = time.time()
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        current_time = time.time()
        if current_time - start_time > max_time:
            print(f'timed out :c at {max_time/60} minutes')
            break

        try:
            load_more_button = driver.find_element("css selector", "button.button-brand")
            load_more_button.click()
            time.sleep(random.randint(200, 300) / 100)
        except se.NoSuchElementException:
            pass

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.randint(200, 300) / 100)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height

def scrape_reddit_thread_url(driver):

    scroll_and_wait(driver)

    html_content = driver.page_source

    soup = BeautifulSoup(html_content, "html.parser")
    post_title_element = soup.find('div', class_='font-semibold')
    post_title = post_title_element.get_text(strip=True)
    clean_post_title = re.sub(r'[\/:*?"<>|]', '_', post_title)

    # Cap the length of the file name to 64 characters
    max_filename_length = 64
    if len(clean_post_title) > max_filename_length:
        clean_post_title = clean_post_title[:max_filename_length]

    comments = soup.find_all('p', class_='')
    comments_text = "<New Comment>".join(comment.get_text(strip=True) for comment in comments)

    users = soup.find_all(
        'a', class_='font-bold text-neutral-content-strong text-12 hover:underline')
    users_text = ", ".join(user.get_text(strip=True) for user in users)

    result = {
        "post_title": post_title,
        "comments": comments_text,
        "users": users_text
    }

    # Write scraped result to a JSON file
    filename = f"out/{clean_post_title}.json"
    print(post_title)
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, indent=4)

    return False


class PostScraper():
    def __init__(self, threads=4):
        self.chrome_driver = driver_manager.ParralelDriverManager(threads)
        self.database = url_database.URLDatabase('seen_posts')

    def scrape(self, urls: set):
        # get unique urls
        self.database.set_current(urls)
        urls = self.database.get_unique()
        if not urls:
            clear = input("Cannot find any unique post urls, type y to clear cache & retry: ")
            if clear == 'y':
                self.database.clear()
                urls = self.database.get_unique()
            else:
                sys.exit()

        #set unique urls
        self.chrome_driver.url_pool = list(urls)

        #start tasks
        self.chrome_driver.parallel_url_task(scrape_reddit_thread_url)

        return True
