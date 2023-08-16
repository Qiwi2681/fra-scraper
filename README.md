# fra-scraper
"Fuck Reddit Admins(API)" Scraper

Scrapes reddit pages to retrive thread text, and usernames.<br>
Focused on memory-optimisation and parralelization.

TODO:
1. rebalance url chunks between threads.
2. Proxy rotation
3. scrape posts from users while waiting for new homepage results.



Working on:
Rebalance url chunks between threads: 
If we turn a fraction of the list into chunks at a time, the threads will be more likley to be synchronized
If we get urls from a stack, we avoid chunking data altogether


The solution(s) I can't do:
1. use requests instead of selenium for small posts.<br>
    ^<br>
    create cache of "long" threads to go over later.

Roadblock:
Reddit has measures in place to prevent this.
    -Comment numbers are obfuscaded, and decoded by javascript
    -In addition to tags which interfere with bs4