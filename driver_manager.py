import time
import random

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


from selenium import webdriver
from selenium.common import exceptions as se
from selenium.webdriver.chrome.service import Service

CHROME_DRIVER = Service(r"D:\chromedriver\chromedriver.exe")
BASE_URL = "https://reddit.com"

class ParralelDriverManager():
    def __init__(self, threads=1):
        self.threads = threads
        self.options = self.get_options()

        self.drivers = []
        self.url_pool = []

    #index driver list
    def __getitem__(self, index):
        return self.drivers[index]

    #selenium options
    @staticmethod
    def get_options():
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        return chrome_options

    # set url
    @staticmethod
    def set_url(driver, url):
        if driver.current_url == url:
            return False
        try:
            if url.startswith('https://'):
                driver.get(url)
            else:
                driver.get(BASE_URL + url)
        except se.WebDriverException:
            print(f"{url} - WebDriverException")

    @staticmethod
    def scroll_and_wait(driver, scrolls_to_perform):
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

        return False

    # configure headless selenium threads
    def start_drivers(self):
        for _ in range(self.threads):
            driver = webdriver.Chrome(service=CHROME_DRIVER, options=self.options)
            self.drivers.append(driver)

    # stop all drivers, clear list
    def stop_drivers(self):
        for driver in self.drivers:
            driver.quit()
        self.drivers = []

    #set urls
    def populate_url_pool(self, urls):
        self.url_pool = urls

    #start parrallel url_tasks
    def parallel_url_task(self, method, *args):
        if not self.drivers:
            self.start_drivers()

        unique = set()

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for driver in self.drivers:
                future = executor.submit(self.url_task, method, driver, *args)
                futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                unique.update(result)

        if unique:
            return unique
        return None

    #iterate over url pool, call method, return output if any
    def url_task(self, method, driver, *args):
        out = set()
        while self.url_pool:
            url = self.url_pool.pop(0)
            self.set_url(driver, url)
            thread_out = method(driver, *args)
            if thread_out:
                out.update(thread_out)
        if out:
            return out
        return None
