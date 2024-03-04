import logging
from datetime import datetime

import scrapy
from bs4 import BeautifulSoup


def get_text(s):
    soup = BeautifulSoup(s.get(), "html.parser")
    return soup.get_text().strip()

class ArgenpropSpider(scrapy.Spider):
    name = "argenprop"
    allowed_domains = ["argenprop.com"]
    start_urls = ["https://www.argenprop.com/casas/venta/hurlingham-hur/3-dormitorios-o-4-dormitorios-o-5-o-mas-dormitorios?1-o-mas-cocheras&180000-250000-dolares"]

    def parse(self, response):
        links = response.css("a[data-item-card]::attr(href)")
        yield from response.follow_all(links, callback=self.parse_listing)
        next_page = response.css("a[rel=next]::attr(href)").get()
        if next_page is not None:
            logging.info("Continuing to next page: %s", next_page)
            yield response.follow(next_page, callback=self.parse)
        else:
            logging.info("No next page found")

    def parse_listing(self, response):
        crawled_at = datetime.now().astimezone().replace(microsecond=0).isoformat()
        price = get_text(response.css(".titlebar__price"))
        address = response.css(".location-container")
        if address:
            address = ", ".join(get_text(address).split("\n"))
            lng = response.css("[data-longitude]::attr(data-longitude)").get().replace(",", ".")
            lat = response.css("[data-latitude]::attr(data-latitude)").get().replace(",", ".")
        else:
            lng = None
            lat = None

        yield {
            "url": response.request.url,
            "price": price,
            "address": address,
            "lng": lng,
            "lat": lat,
            "crawled_at": crawled_at,
        }


