from selenium import webdriver
from selenium.common import exceptions as se
from selenium.webdriver.chrome.service import Service

CHROME_DRIVER = Service(r"C:\path\to\Chromedriver.exe")
BASE_URL = "https://reddit.com"

class ParralelDriverManager():
    def __init__(self, threads=1):
        self.threads = threads
        self.options = self.get_options()
        self.drivers = []

    @staticmethod
    def get_options():
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")
        return chrome_options

    # configure headless selenium threads
    def start_drivers(self):
        for _ in range(self.threads):
            driver = webdriver.Chrome(service=CHROME_DRIVER, options=self.options)
            self.drivers.append(driver)

    def stop_drivers(self):
        for driver in self.drivers:
            driver.quit()
        self.drivers = []

    def set_url(self, index, url):
        target = self.drivers[index]
        try:
            if url.startswith('https://'):
                target.get(url)
            else:
                target.get(BASE_URL + url)
        except se.WebDriverException:
            print(f"Thread {index} - WebDriverException")

if __name__ == "__main__":
    a = ParralelDriverManager()
    a.start_drivers()
    a.stop_drivers()
