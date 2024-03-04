import json
import logging
import re
from datetime import datetime
from urllib.parse import urljoin

import scrapy
from bs4 import BeautifulSoup


def get_text(s):
    soup = BeautifulSoup(s.get(), "html.parser")
    return soup.get_text().strip()

class MercadoLibreSpider(scrapy.Spider):
    name = "mercadolibre"
    allowed_domains = ["mercadolibre.com.ar", "api.mercadolibre.com"]
    start_urls = ["https://inmuebles.mercadolibre.com.ar/casas/venta/mas-de-3-dormitorios/bsas-gba-oeste/hurlingham/hurlingham/_PriceRange_180000USD-250000USD_NoIndex_True_PARKING*LOTS_1-*#applied_filter_id%3DPARKING_LOTS%26applied_filter_name%3DCocheras%26applied_filter_order%3D9%26applied_value_id%3D1-*%26applied_value_name%3D1-*%26applied_value_order%3D6%26applied_value_results%3DUNKNOWN_RESULTS%26is_custom%3Dtrue"]

    def parse(self, response):
        links = response.css(".ui-search-link__title-card.ui-search-link::attr(href)").getall()
        for link in links:
            match = re.search(r'MLA-\d+', link)
            if match:
                item_id = "".join(match.group().split("-"))
                api_url = urljoin("https://api.mercadolibre.com/items/", item_id)
                yield response.follow(api_url, callback=self.parse_listing, cb_kwargs=dict(url=link))
            else:
                logging.error("Could not extract item ID from URL %s", link)

        next_page = response.css(".andes-pagination__button--next a::attr(href)").get()
        if next_page is not None:
            logging.info("Continuing to next page: %s", next_page)
            yield response.follow(next_page, callback=self.parse)
        else:
            logging.info("No next page found")

    def parse_listing(self, response, url):
        crawled_at = datetime.now().astimezone().replace(microsecond=0).isoformat()
        data = json.loads(response.text)
        # item_id = response.request.url
        # address = response.css(".location-container")
        # if address:
        #     address = get_text(address)
        #     lng = response.css("[data-longitude]::attr(data-longitude)").get()
        #     lat = response.css("[data-latitude]::attr(data-latitude)").get()
        # else:
        #     lng = None
        #     lat = None

        yield {
            "url": url,
            "price": "{} {}".format(data["currency_id"], data["price"]),
            "address": "{}, {}".format(data["location"]["address_line"], data["location"]["neighborhood"]["name"]),
            # coordinates not returned in API :(
            # "lng": lng,
            # "lat": lat,
            "api_url": response.request.url,
            "crawled_at": crawled_at,
        }


