import sys
import home_scraper
import subreddit_scraper
import post_scraper

if __name__ == "__main__":
    HOMEPAGE_SCROLLS = 10 # 40-180 subreddits
    SUBPAGE_SCROLLS = 5 # 20-40 posts per sub
    # 400 - 7200 urls per scrape

    #home page
    homepage = home_scraper.HomePageCrawler(HOMEPAGE_SCROLLS, threads=4)
    subreddits = homepage.get_urls()
    if not subreddits:
        clear = input("Cannot find any unique subreddits, type y to clear cache & retry: ")
        if clear == 'y':
            homepage.database.clear()
            subreddits = homepage.get_urls()
        else:
            sys.exit()

    #subreddits
    subpage = subreddit_scraper.SubRedditCrawler(SUBPAGE_SCROLLS, threads=4)
    posts = subpage.get_urls(list(subreddits))

    #post scraper
    scraper = post_scraper.PostScraper(threads=4)
    scraper.scrape(list(posts))
