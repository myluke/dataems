# coding=utf-8
from pymongo import MongoClient
import logging
import pymysql
import requests
import json

MySQL_HOST = '192.168.1.240'
MySQL_PORT = 3306

def check():
    mysql_db = pymysql.connect(host=MySQL_HOST, port=MySQL_PORT, user='dataems', password='Zetta12345', database='scrapymanager', charset='utf8')
    cursor = mysql_db.cursor()
    cursor.execute("SELECT * from sp_anjuke where source_web='fang' or source_web='anjuke' and length(house_lat)<=1")
    rows = cursor.fetchall()
    print(cursor.rowcount)
    for row in rows:
        ajk_id= row[0]
        ajk_name=row[1]
        gps=get_gps(ajk_name)
        if gps is not None:
            lat = gps["lat"]
            lng = gps["lng"]
            try:
                cursor.execute("UPDATE sp_anjuke SET house_lat=%s,house_lng=%s WHERE id=%s ",(lat,lng,ajk_id))
                mysql_db.commit()
                print(ajk_id,ajk_name,lat,lng)
            except Exception as e:
                print(e)
        else: 
            lat = ""
            lng = ""
            print(ajk_id,ajk_name,lat,lng)
    cursor.close()
    mysql_db.close()

def get_gps(txt):
        s = requests.session()  
        url = 'http://api.map.baidu.com/place/v2/suggestion?query='+txt+'&region=上海&city_limit=true&output=json&ak=EGOQlsLbQxqQZ9lYTZHS1akgvs0K5hT9'
        header = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'}  
        response = s.get(url, headers = header, timeout = 20)  
        try:
            data = json.loads(response.text)  
        except Exception as e:
            print(e)
        if data is not None:
            print(data)  
            if len(data['result'])>0:
                if 'name' in data['result'][0].keys() and 'location' in data['result'][0].keys():
                    dictgps = {"name":data['result'][0]['name'],"lat":data['result'][0]['location']['lat'],"lng":data['result'][0]['location']['lng']}
                    #print(dictgps)
                    return dictgps
                else:    
                    return None
            else:
                return None
        else:
            return None


if __name__ == '__main__':
    check()
