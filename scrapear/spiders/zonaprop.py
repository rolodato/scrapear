import logging
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import scrapy
from bs4 import BeautifulSoup


def get_text(s):
    soup = BeautifulSoup(s.get(), "html.parser")
    return soup.get_text().strip()

class ZonapropSpider(scrapy.Spider):
    name = "zonaprop"
    allowed_domains = ["zonaprop.com.ar"]
    start_urls = ["https://www.zonaprop.com.ar/casas-venta-hurlingham-mas-de-2-banos-desde-2-hasta-3-habitaciones-mas-de-1-garage-180000-250000-dolar.html"]

    def parse(self, response):
        links = response.css("[data-to-posting]::attr('data-to-posting')")
        yield from response.follow_all(links, callback=self.parse_listing)
        next_page = response.css("[data-qa='PAGING_NEXT']::attr(href)").get()
        if next_page is not None:
            logging.info("Continuing to next page: %s", next_page)
            yield response.follow(next_page, callback=self.parse)
        else:
            logging.info("No next page found")

    def parse_listing(self, response):
        crawled_at = datetime.now().astimezone().replace(microsecond=0).isoformat()
        price = response.css(".price-value span span")
        map_url = response.css("#static-map:not(.static-map-no-location)")
        if map_url:
            address = get_text(response.css("#map-section h4"))
            [lat, lng] = parse_qs(urlparse(map_url.attrib["src"]).query)["center"][0].split(",")

        else:
            address = None
            [lng, lat] = [None, None]
        yield {
            "url": response.request.url,
            "price": get_text(price),
            "address": address,
            "lng": lng,
            "lat": lat,
            "crawled_at": crawled_at,
        }


