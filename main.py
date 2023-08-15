import home_scraper
import subreddit_scraper
import post_scraper

if __name__ == "__main__":
    HOMEPAGE_SCROLLS = 10 # 40-180 subreddits
    SUBPAGE_SCROLLS = 5 # 20-40 posts per sub
    # 400 - 7200 urls per scrape

    #init scrapers
    homepage = home_scraper.HomePageCrawler(HOMEPAGE_SCROLLS, threads=4)
    subpage = subreddit_scraper.SubRedditCrawler(SUBPAGE_SCROLLS, threads=4)

    #get urls
    subreddits = homepage.get_urls()
    posts = subpage.getURLs(list(subreddits))

    #scrape
    scraper = post_scraper.PostScraper(threads=4)
    scraper.scrape(list(posts))
