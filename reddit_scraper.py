import time
import random
import driver_manager

class RedditScraper(driver_manager.ParralelDriverManager):
    def __init__(self, threads=1):
        super().__init__(threads)


