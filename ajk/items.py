# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AjkItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    house_name = scrapy.Field()
    house_price = scrapy.Field()
    house_bdyear = scrapy.Field()
    house_bdaddr = scrapy.Field()
    house_bddist = scrapy.Field()
    house_lat = scrapy.Field()
    house_lng = scrapy.Field()
    craw_date = scrapy.Field()
    source_web = scrapy.Field()
