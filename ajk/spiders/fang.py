# -*- coding: utf-8 -*-
import scrapy
import datetime
import time
from ajk.items import AjkItem as ajk
import random
import scrapy.http.response
import re
import requests
import json
import re


class FangSpider(scrapy.Spider):
    name = 'fang'
    allowed_domains = ['fang.com']
    start_urls = ['http://esf.sh.fang.com/housing']

    def parse(self, response):
        district_name = response.xpath('//div[@class="qxName"]/a[not(@class="org bold") and not(contains(text(),"周边"))]/text()').extract()
        district_url = response.xpath('//div[@class="qxName"]/a[not(@class="org bold") and not(contains(text(),"周边"))]/@href').extract()
        for name, url in zip(district_name, district_url):
            print("开始区=========")
            print(url)
            yield scrapy.Request(url=response.urljoin(url), callback=self.town)
            time.sleep(random.randint(1,3))

    def town(self,response):
        town_names = response.xpath('//p[@id="shangQuancontain"]/a[not(@class="org bold")]/text()').extract() 
        town_urls = response.xpath('//p[@id="shangQuancontain"]/a[not(@class="org bold")]/@href').extract() 
        for name, url in zip(town_names, town_urls):
            print("开始镇=========")
            print(url)
            yield scrapy.Request(url=response.urljoin(url),callback=self.town_data)
            time.sleep(random.randint(1,3))

    def town_data(self,response):
        ershou = ajk()
        data_area = response.xpath('//div[@class="houseList"]/div[@class="list rel"]')
        names = []
        prices = []
        bdyears = []
        bdaddrs = []
        lats = []
        lngs = []
        cdates=[]
        for data in data_area:
            print("开始小区=========")
            name = data.xpath('dl[@class="plotListwrap clearfix"]/dd/p/a[@class="plotTit"]/text()').extract()         
            price = data.xpath('div[@class="listRiconwrap"]/p[@class="priceAverage"]/span[1]/text()').extract()
            bdaddr = data.xpath('dl[@class="plotListwrap clearfix"]/dd/p[2]/a[1]/text()').extract()
            bddistrict = data.xpath('dl[@class="plotListwrap clearfix"]/dd/p[2]/a[1]/text()').extract()
            bdyear =     data.xpath('dl[@class="plotListwrap clearfix"]/dd/ul[@class="sellOrRenthy clearfix"]/li[3]/text()').extract()
            if name:
                names.append(name[0].strip().rstrip().lstrip())
                lats.append(" ")
                lngs.append(" ")
                    
                bdaddrs.append(bddistrict[0])

                if bdyear:
                    bdyears.append(bdyear[0])
                else:
                    bdyears.append('9999')

                if price:
                    tmp = re.findall("[-+]?\d+[\.]?\d*",price[0].strip().rstrip().lstrip())
                    if tmp:
                        prices.append(tmp[0])
                    elif not tmp:
                        prices.append('暂无均价')
                elif not price:
                    prices.append('暂无均价')
                dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cdates.append(dt)
            
        for block_name, block_price,block_bdyear,block_bdaddr,block_lat,block_lng,block_date in zip(names, prices, bdyears,bdaddrs,lats,lngs,cdates):
            ershou['house_name'] = block_name
            ershou['house_price'] = block_price
            ershou['house_bdyear'] = block_bdyear
            ershou['house_bdaddr'] = block_bdaddr
            ershou['house_lat'] = block_lat
            ershou['house_lng'] = block_lng
            ershou['craw_date'] = block_date
            ershou['source_web'] = "fang"
            yield ershou
            next_link = response.xpath('//div[@class="fanye gray6"]/a[contains(text(), "下一页")]/@href').extract()
            if next_link:
                url = next_link[0]
                print('next page ============='+url)
                time.sleep(random.randint(1,3))
                yield scrapy.Request(url=response.urljoin(url), callback=self.town_data)
