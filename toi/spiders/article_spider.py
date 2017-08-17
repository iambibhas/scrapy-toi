import scrapy
import itertools
import datetime
import calendar
from dateutil import parser


MONTHS = range(1, 13)
YEARS = range(2001, 2018)
BASE_DATE = datetime.date(1899, 12, 30)
CURRENT_DATE = datetime.date.today()
VALID_END_DATE = CURRENT_DATE - datetime.timedelta(days=2)


class ArticleSpider(scrapy.Spider):
    name = "article"

    def start_requests(self):
        monthly_url_template = "http://timesofindia.indiatimes.com/{year}/{month}/{date}/archivelist/year-{year},month-{month},starttime-{delta}.cms"
        year_month_combos = list(itertools.product(YEARS, MONTHS))
        for combo in year_month_combos:
            year, month = combo
            _, days = calendar.monthrange(year, month)
            for date in range(1, days+1):
                compare_date = datetime.date(year, month, date)
                if compare_date > VALID_END_DATE:
                    continue
                dt_delta = compare_date - BASE_DATE
                delta = dt_delta.days
                url = monthly_url_template.format(year=year, month=month, date=date, delta=delta)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if 'starttime' in response.url:
            # it's an archive page
            for article_url in response.xpath('//a[contains(@href, "articleshow")]/@href').extract():
                if 'timesofindia.indiatimes.com' not in article_url:
                    article_url = 'http://timesofindia.indiatimes.com' + article_url
                yield scrapy.Request(url=article_url, callback=self.parse)
        elif 'articleshow' in response.url:
            # this is an article page
            title = response.xpath('//h1[@class="heading1"]/text()').extract_first()

            if not title:
                raise Exception('No Title Found!')

            published_dt = response.xpath('//span[@itemprop="datePublished"]/text()').extract_first()

            if not published_dt:
                published_dt_text = response.xpath('//span[@class="time_cptn"]/text()').extract_first()
                if published_dt_text:
                    dt_parts = published_dt_text.split(' | ')
                    if len(dt_parts) > 0:
                        published_dt = dt_parts[-1]

            if not published_dt:
                dt_parts = response.xpath('//span[@class="time_cptn"]//span/text()').extract()
                if len(dt_parts) > 0:
                    published_dt = dt_parts[-1]

            parsed_dt = ''
            if published_dt:
                published_dt = published_dt.replace('Updated: ', '').replace('.', ":")
                try:
                    parsed_dt = parser.parse(published_dt).isoformat()
                except:
                    raise Exception('Cannot parse datetime: %s' % published_dt)

            body = response.xpath('//div[contains(@class, "article_content") or @itemprop="articleBody"]').extract_first()

            yield {'url': response.url, 'title': title, 'published_dt': parsed_dt, 'body': body}
