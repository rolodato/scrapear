# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import os

import googlemaps
from dotenv import load_dotenv
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import logging

load_dotenv()

class TravelTimePipeline:
    gmaps = googlemaps.Client(key=os.environ["GOOGLE_MAPS_API_KEY"])
    san_martin = "Estación Hurlingham del FFCC San Martín"
    urquiza = "Rubén Darío, Hurlingham"
    max_travel_time = 15 * 60
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if not adapter["lat"] or not adapter["lng"]:
            logging.info(f"Item {item} has no location, passing through anyway")
            return item

        origin = ([adapter["lat"], adapter["lng"]])
        san_martin_travel_time = gmaps.directions(
            origin,
            destination=san_martin,
            mode="walking",
        )[0]["legs"][0]["duration"]

        urquiza_travel_time = gmaps.directions(
            origin,
            destination=urquiza,
            mode="walking",
        )[0]["legs"][0]["duration"]

        if san_martin_travel_time["value"] > max_travel_time and urquiza_travel_time["value"] > max_travel_time:
            raise DropItem(f"Dropping {item}, travel time too long")

        adapter["san_martin_travel_time"] = san_martin_travel_time["text"]
        adapter["urquiza_travel_time"] = urquiza_travel_time["text"]
        return item
