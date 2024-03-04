import scrapy


class ZonapropSpider(scrapy.Spider):
    name = "zonaprop"
    allowed_domains = ["zonaprop.com.ar"]
    start_urls = ["https://www.zonaprop.com.ar"]

    def parse(self, response):
        pass
