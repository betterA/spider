import requests
from bs4 import BeautifulSoup
from config import *
import pymongo
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def get_one_page(url):
    try:
        response = requests.get(url,headers=HEADERS)
        if response.status_code == 200:
            return response.text
        return None
    except:
        return None

def parse_one_page(html):
    soup = BeautifulSoup(html, 'lxml')
    title_list = soup.find_all(class_= 'pl2')
    for i in title_list:
        yield {
        'book_url':i.a['href'],
        'book_name':i.a['title'],
        'book_detail': i.find_next_sibling().text,
        'book_rat':i.find_next_sibling().find_next_sibling().find(class_='rating_nums').text
        }

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
         print('存入成功')
         return True
    return False

if __name__ == '__main__':
    for i in PAGE_OF_WEB:
        url = f"https://book.douban.com/top250?start={i}"
        print(url)
        html = get_one_page(url)
        for item in parse_one_page(html):
            if item:
                save_to_mongo(item)
