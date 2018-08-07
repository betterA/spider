import requests
import json
import re
from config import *
from bs4 import BeautifulSoup
import time
import pymongo

def get_music_page(url,title):
    response = requests.post(url,PARAM,headers=HEADERS)
    r_json = response.json()
    hot_content = r_json.get("hotComments")
    contents = [item.get('content') for item in hot_content]
    return {
            'title':title,
            'content':contents
        }


def get_music_list(url):
    rs = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(rs.text, 'lxml')
    detail_list = soup.select('ul.f-hide li a')
    for i in detail_list:
        music_id = re.findall('(\d+)',i['href'])
        content_url = f'https://music.163.com/weapi/v1/resource/comments/R_SO_4_{music_id[0]}?csrf_token='
        print(content_url)
        title = i.string
        time.sleep(1)
        result = get_music_page(content_url,title)
        if result:
            save_to_mongo(result)

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
         print('存入成功',result)
         return True
    return False


client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
url = 'https://music.163.com/playlist?id=2168333836'
get_music_list(url)

