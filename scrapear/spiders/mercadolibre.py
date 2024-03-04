import json
import logging
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs

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
                yield response.follow(api_url, callback=self.parse_api_data, cb_kwargs=dict(url=link))
            else:
                logging.error("Could not extract item ID from URL %s", link)

        next_page = response.css(".andes-pagination__button--next a::attr(href)").get()
        if next_page is not None:
            logging.info("Continuing to next page: %s", next_page)
            yield response.follow(next_page, callback=self.parse)
        else:
            logging.info("No next page found")

    def parse_api_data(self, response, url):
        data = json.loads(response.text)
        api_data = {
            "url": url,
            "price": "{} {}".format(data["currency_id"], data["price"]),
            "address": "{}, {}".format(data["location"]["address_line"], data["location"]["neighborhood"]["name"]),
            "api_url": response.request.url,
        }
        yield response.follow(data["permalink"], meta=api_data, callback=self.parse_html_data)

    def parse_html_data(self, response):
        crawled_at = datetime.now().astimezone().replace(microsecond=0).isoformat()
        map_url = urlparse(response.css("#ui-vip-location__map img::attr(src)").get())
        [lng, lat] = parse_qs(map_url.query)["center"][0].split(",")
        yield {
            "url": response.meta.get("url"),
            "price": response.meta.get("price"),
            "address": response.meta.get("address"),
            "lng": lng,
            "lat": lat,
            "api_url": response.meta.get("api_url"),
            "crawled_at": crawled_at,
        }
