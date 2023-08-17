# fra-scraper
"Fuck Reddit Admins(API)" Scraper

Scrapes reddit pages to retrive thread text, and usernames.<br>
Focused on memory-optimisation and parralelization.

TODO:
1. Proxy rotation
2. scrape posts from users while waiting for new homepage results.



v1.1:
Rebalance url chunks between threads:<br>
    -get urls from a stack, avoid chunking data altogether<br>


Cant DO:
1. use requests instead of selenium for small posts.<br>
    ^<br>
    create cache of "long" threads to go over later.

Roadblock:
Reddit has measures in place to prevent this.<br>
    -Comment numbers are obfuscaded, and decoded by javascript<br>
    -In addition to tags which interfere with bs4<br>