# Scraping articles from TOI (you know which)

## How?

I checked their [archive page](http://timesofindia.indiatimes.com/archive.cms),
and it seems that the daily archive page urls are
generated using day, month, year and another certain delta component, which can
also be calculated (got the calculation from their JS script).
So I'm just generating all the daily archive pages and then
crawling them for articles.

## How to run this

 - clone the repo
 - create virtualenv and install the requirements.txt
 - run `scrapy crawl article -o outputfile.json`
