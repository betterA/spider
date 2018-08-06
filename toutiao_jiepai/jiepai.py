import requests
from urllib.parse import urlencode
from requests.exceptions import RequestException
import json
from bs4 import BeautifulSoup 
import re
from config import *
import pymongo
import os
from hashlib import md5
from multiprocessing import Pool
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 1,
        'from': 'search_tab'
    }
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'}
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        pass
    except RequestException:
        print('error')
        pass

def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')

def get_page_detail(url):
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        pass
    except RequestException:
        print('error')
        pass  

def parse_page_detail(html,url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    images_pattern = re.compile('gallery: JSON.parse\(\"(.*?)\"\),')
    result = re.search(images_pattern, html)
    if result:
        newResult = result.group(1).replace('\\\\', '#')
        newResult = newResult.replace('\\', '')
        newResult = newResult.replace('#', '\\\\')
        newResult = newResult.replace('\/', '/')
       
        data = json.loads(newResult)
        
        sub_images = data.get('sub_images')
        images = [item.get('url') for item in sub_images]
        for url in images:download_image(url)
        return {
            'title':title,
            'url':url,
            'images':images
        }

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
         print('存入成功',result)
         return True
    return False

def download_image(url):
    print("正在下载",url)
    headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'}
   
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            save_image(response.content)
        pass
    except RequestException:
        print('图片error')
        pass

def save_image(content):
    file_path = f"{os.getcwd()}/{md5(content)}.jpg"
    if not os.path.exists(file_path):
        with open (file_path, 'wb') as f:
            f.write(content)
            f.close()

def main(offset):
    html = get_page_index(offset, '街拍')
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html,url)
            if result:
                save_to_mongo(result)


if __name__ == '__main__':
    groups = [x*20 for x in range(1,21)]
    pool = Pool()
    pool.map(main, groups)
    