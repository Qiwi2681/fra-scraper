import re
import time
import json
import random

from concurrent.futures import ThreadPoolExecutor
from selenium.common import exceptions as se
from bs4 import BeautifulSoup

import driver_manager


BASE_URL = "https://reddit.com"

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

def scrape_reddit_thread_url(driver, urls, chunk_idx):

    for url in urls:
        print(f"Thread {chunk_idx} - Scraping URL: {url}")

        try:
            if url.startswith('https://'):
                driver.get(url)
            else:
                driver.get(BASE_URL + url)
        except se.WebDriverException:
            print(f"Thread {chunk_idx} - WebDriverException")
            continue

        sub_pattern = r"/r/(\w+)/"
        subreddit = re.search(sub_pattern, url)

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
        comments_text = ", ".join(comment.get_text(strip=True) for comment in comments)

        users = soup.find_all(
            'a', class_='font-bold text-neutral-content-strong text-12 hover:underline')
        users_text = ", ".join(user.get_text(strip=True) for user in users)

        result = {
            "subreddit": str(subreddit),
            "post_title": post_title,
            "comments": comments_text,
            "users": users_text
        }

        # Write scraped result to a JSON file
        filename = f"out/{clean_post_title}.json"
        print(f"Thread {chunk_idx} - Writing to file: {filename}")
        with open(filename, "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, indent=4)

    return True


class PostScraper():
    def __init__(self, threads = 1):
        self.chrome_driver = driver_manager.ParralelDriverManager(threads)

    #assign each thread a chunk of urls, save them in out/ as we go
    #this is the "main" function, where the scraped data is being saved to disk
    def scrape(self, urls: list):
        self.chrome_driver.start_drivers()
        worker_count = len(self.chrome_driver.drivers)
        chunk_size = len(urls) // worker_count
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            for chunk_idx in range(worker_count):
                chunk_start = chunk_idx * chunk_size
                if chunk_idx != worker_count - 1:
                    chunk_end = (chunk_idx + 1) * chunk_size
                else:
                    chunk_end = len(urls)
                chunk_urls = list(urls)[chunk_start:chunk_end]  # Convert set to list here
                executor.submit(scrape_reddit_thread_url,
                                self.chrome_driver.drivers[chunk_idx], chunk_urls, chunk_idx)

        self.chrome_driver.stop_drivers()
        return True
    