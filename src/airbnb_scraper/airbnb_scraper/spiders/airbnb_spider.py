import scrapy


class AirbnbSpiderSpider(scrapy.Spider):
    name = 'airbnb_spider'
    allowed_domains = ['pythonscraping.com']
    start_urls = ['http://pythonscraping.com/']

    def parse(self, response):
        pass
