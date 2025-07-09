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
    # start_urls = ["https://www.zonaprop.com.ar/casas-venta-hurlingham-mas-de-2-banos-desde-2-hasta-3-habitaciones-mas-de-1-garage-180000-250000-dolar.html"]

    def start_requests(self):
        yield scrapy.Request("https://www.zonaprop.com.ar/casas-venta-hurlingham-mas-de-2-banos-desde-2-hasta-3-habitaciones-mas-de-1-garage-180000-250000-dolar.html", meta={"playwright": True})

    def parse(self, response):
        links = response.css("[data-to-posting]::attr('data-to-posting')")
        yield from response.follow_all(links, callback=self.parse_listing, meta={"playwright": True})
        next_page = response.css("[data-qa='PAGING_NEXT']::attr(href)").get()
        if next_page is not None:
            logging.info("Continuing to next page: %s", next_page)
            yield response.follow(next_page, callback=self.parse)
        else:
            logging.info("No next page found")

    def parse_listing(self, response):
        crawled_at = datetime.now().astimezone().replace(microsecond=0).isoformat()
        price = response.css(".price-value span span")
        # map_url = response.css("#static-map:not(.static-map-no-location)")
        # if map_url:
        #     address = get_text(response.css("#map-section h4"))
        #     [lat, lng] = parse_qs(urlparse(map_url.attrib["src"]).query)["center"][0].split(",")
        # else:
        #     address = None
        #     [lng, lat] = [None, None]

        bathrooms = get_text(response.css(".icon-bano"))
        m2_total = get_text(response.css(".icon-stotal"))
        m2_covered = get_text(response.css(".icon-scubierta"))
        parking_spaces = get_text(response.css(".icon-cochera"))
        age = get_text(response.css(".icon-antiguedad"))
        publisher = get_text(response.css("#reactPublisherData h3"))

        yield {
            "url": response.request.url,
            "price": get_text(price),
            # "address": address,
            "m2_total": m2_total,
            "m2_covered": m2_covered,
            "bathrooms": bathrooms,
            "parking_spaces": parking_spaces,
            "age": age,
            "publisher": publisher,
            # "lng": lng,
            # "lat": lat,
            "crawled_at": crawled_at,
        }


