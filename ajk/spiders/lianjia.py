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


class LianjiaSpider(scrapy.Spider):
    name = 'lianjia'
    allowed_domains = ['lianjia.com']
    start_urls = ['http://sh.lianjia.com/xiaoqu']

    def parse(self, response):
        district_name = response.xpath('//div[@class="option-list gio_district"]/a[@class!="on" and not(contains(text(),"周边"))]/text()').extract()
        district_url = response.xpath('//div[@class="option-list gio_district"]/a[@class!="on" and not(contains(text(),"周边"))]/@href').extract()
        for name, url in zip(district_name, district_url):
            print("开始区=========")
            print(url)
            yield scrapy.Request(url=response.urljoin(url), callback=self.town)
            time.sleep(random.randint(1,3))

    def town(self,response):
        town_names = response.xpath('//div[@class="option-list sub-option-list gio_plate"]/a[@class!="on"]/text()').extract() 
        town_urls = response.xpath('//div[@class="option-list sub-option-list gio_plate"]/a[@class!="on"]/@href').extract() 
        for name, url in zip(town_names, town_urls):
            print("开始镇=========")
            print(url)
            yield scrapy.Request(url=response.urljoin(url),callback=self.town_data)
            time.sleep(random.randint(1,3))

    def town_data(self,response):
        ershou = ajk()
        data_area = response.xpath('//div[@class="list-wrap"]/ul[@class="house-lst"]/li')
        names = []
        prices = []
        bdyears = []
        bdaddrs = []
        lats = []
        lngs = []
        cdates=[]
        for data in data_area:
            name = data.xpath('div[@class="info-panel"]/h2/a/text()').extract()         
            price = data.xpath('div[@class="info-panel"]/div[@class="col-3"]/div[@class="price"]/span[@class="num"]/text()').extract()
            bdaddr = data.xpath('div[@class="info-panel"]/div[@class="col-1"]/div[@class="where"]/a[@class="actshowMap_list"]/@xiaoqu').extract()
            bddistrict = data.xpath('div[@class="info-panel"]/div[@class="col-1"]/div[@class="where"]/a[@class="actshowMap_list"]/@districtname').extract()
            bdyear =     data.xpath('div[@class="info-panel"]/div[@class="col-1"]/div[@class="other"]/div[@class="con"]/text()').extract()
            if name:
                names.append(name[0])
                if bdaddr[0]:
                    tmp = re.findall("[-+]?\d+[\.]?\d*",bdaddr[0])
                    if tmp:
                        if tmp[0]:
                            lngs.append(tmp[0])
                        elif not tmp[0]:
                            lngs.append(" ")
                        if tmp[1]:
                            lats.append(tmp[1])
                        elif not tmp[1]:
                            lats.append(" ")
                    elif not tmp:
                        lats.append(" ")
                        lngs.append(" ")
                elif not bdaddr[0]:
                    lats.append(" ")
                    lngs.append(" ")
                    

                bdaddrs.append(bddistrict[0])

                if (len(bdyear)>=4):
                    if bdyear[3]:
                        tmp=bdyear[3].strip().rstrip().lstrip()
                        if tmp:
                            bdyears.append(tmp)
                        elif not tmp:
                            bdyears.append('9999')
                    elif not bdyear[3]:
                        bdyears.append('9999')
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
            ershou['source_web'] = "lianjia"
            yield ershou
            next_link = response.xpath('//div[@class="page-box house-list-page-box"]/a[contains(text(), "下一页")]/@href').extract()
            print(next_link)
            if next_link:
                url = next_link[0]
                print('next page ============='+url)
                time.sleep(random.randint(1,3))
                yield scrapy.Request(url=response.urljoin(url), callback=self.town_data)
