# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
import pymysql

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017

MySQL_HOST = '192.168.1.240'
MySQL_PORT = 3306

class AjkPipeline(object):
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client['ajk']
    collection_name = 'sanshou'

    mysql_db = pymysql.connect(host=MySQL_HOST, port=MySQL_PORT, user='dataems', password='Zetta12345', database='scrapymanager',
                               charset='utf8')
    cursor = mysql_db.cursor()

    # 存入MongoDB
    # def process_item(self, item, spider):
    #     self.db[self.collection_name].insert_one(dict(item))
    #     return item
    # 存入MySQL
    def process_item(self, item, spider):
        sql = 'insert into sp_anjuke(house_name, house_price, house_bdyear, house_bdaddr,house_bddist,house_lat,house_lng,craw_date,source_web) values (%s,%s, %s, %s, %s,%s,%s,%s,%s)'
        name = item['house_name']
        price = item['house_price']
        bdyear = item['house_bdyear']
        bdaddr = item['house_bdaddr']
        bddist = item['house_bddist']
        lat = item['house_lat']
        lng = item['house_lng']
        cdate = item['craw_date']
        source = item['source_web']
        print(name, price,bdyear, bdaddr,bddist,lat,lng,cdate)
        try:
            self.cursor.execute(sql, (name, price,bdyear,bdaddr,bddist,lat,lng,cdate,source))
            self.mysql_db.commit()
        except:
            self.mysql_db.rollback()
        return item

    def close_spider(self, spider):
        self.mysql_db.close()
