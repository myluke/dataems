# -*- coding: utf-8 -*-
import scrapy


class SinaSpider(scrapy.Spider):
    name = 'sina'
    allowed_domains = ['sina.com']
    start_urls = ['http://sina.com/']

    def parse(self, response):
        pass
