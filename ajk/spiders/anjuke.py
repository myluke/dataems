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

class AnjukeSpider(scrapy.Spider):
    second = []
    page_num = 1
    name = 'anjuke'
    url = 'http://shanghai.anjuke.com/community/?from=navigation'
#   handle_httpstatus_list = [414]
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch',
        'accept-language': 'zh-CN,zh;q=0.8',
        'q': '0.8',
        "Connection": "keep-alive",
        'cache-control': 'max - age = 0',
        'referer': 'http://shanghai.anjuke.com',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    }

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        district_name = response.xpath('//span[@class="item-title" and contains(text(), "区域")]/../span[@class="elems-l"]/a[@class="" and @href!="https://shanghai.anjuke.com/community/shanghaizhoubian"]/text()').extract()
        district_url = response.xpath('//span[@class="item-title" and contains(text(), "区域")]/../span[@class="elems-l"]/a[@class="" and @href!="https://shanghai.anjuke.com/community/shanghaizhoubian"]/@href').extract()
        for name, url in zip(district_name, district_url):
            print("开始区========")
            print(url)
            yield scrapy.Request(url=url, headers=self.headers, callback=self.town, meta={'name': name})
            time.sleep(random.randint(1,3))

    def town(self, response):
        global page_num
        town_names = response.xpath('//div[@class="sub-items"]/a[@data-id!="全部"]/@data-id').extract()
        town_urls = response.xpath('//div[@class="sub-items"]/a[@data-id!="全部"]/@href').extract()
        page_num  = 1
        for name, url in zip(town_names, town_urls):
            print("开始镇==========="+ url)
            yield scrapy.Request(url=url, headers=self.headers, callback=self.town_data)
            time.sleep(random.randint(1, 3))

    def town_data(self, response):
        ershou = ajk()
        data_area = response.xpath('//div[@_soj="xqlb"]')
        print(len(data_area))
        global page_num
        names = []
        prices = []
        bdyears = []
        bdaddrs = []
        lats = []
        lngs = []
        cdates=[]
        for data in data_area:
            name = data.xpath('div[@class="li-info"]/h3/a/text()').extract()
            price = data.xpath('div[@class="li-side"]/p/strong/text()').extract()
            bdyear = data.xpath('div[@class="li-info"]/p[@class="date"]/text()').extract()
            bdaddr = data.xpath('div[@class="li-info"]/address/text()').extract()
            if name:
                names.append(name[0])
#                gpslocation = self.get_gps(name[0])
#                if gpslocation:
#                    lats.append(gpslocation['lat'])
#                    lngs.append(gpslocation['lng'])
#                elif not gpslocation:
#                    lats.append(' ')
#                    lngs.append(' ')
            lats.append(' ')
            lngs.append(' ')

            if price:
                prices.append(price[0])
            elif not price:
                prices.append('暂无均价')
            if bdyear:
                bdyears.append(self.get_year(bdyear[0]))
            elif not bdyear:
                bdyears.append('9999')
            if bdaddr:
                bdaddrs.append(bdaddr[0].strip().lstrip().rstrip())
            elif not bdaddr:
                bdaddrs.append('暂无地址')
            dt=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
            cdates.append(dt)
        assert len(names) == len(prices)
        for block_name, block_price,block_bdyear,block_bdaddr,block_lat,block_lng,block_date in zip(names, prices, bdyears,bdaddrs,lats,lngs,cdates):
            ershou['house_name'] = block_name
            ershou['house_price'] = block_price
            ershou['house_bdyear'] = block_bdyear
            ershou['house_bdaddr'] = block_bdaddr
            ershou['house_lat'] = block_lat 
            ershou['house_lng'] = block_lng 
            ershou['craw_date'] = block_date
            ershou['source_web'] = "anjuke" 
            yield ershou
        next_link = response.xpath('//div[@class="multi-page"]/a[contains(text(), "下一页")]/@href').extract()
        print(next_link)
        if next_link:
            url = next_link[0]
            page_num = page_num + 1
            print('next page ============='+url)
            time.sleep(random.randint(1,3))
            yield scrapy.Request(url=url, headers=self.headers, callback=self.town_data)

    def get_year(self,txt):
         pattern = re.compile(r"\d{4}")
         res = re.findall(pattern,txt)
         return res

    def get_gps(self,txt):
        s = requests.session()  
        url = 'http://api.map.baidu.com/place/v2/suggestion?query='+txt+'&region=上海&city_limit=true&output=json&ak=EGOQlsLbQxqQZ9lYTZHS1akgvs0K5hT9'
        header = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'}  
        response = s.get(url, headers = header, timeout = 20)  
#        print(response.text)  
        data = json.loads(response.text)  
        dictgps = {"name":data['result'][0]['name'],"lat":data['result'][0]['location']['lat'],"lng":data['result'][0]['location']['lng']}
#       print(dictgps)
        return dictgps


