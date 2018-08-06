import requests
from bs4 import BeautifulSoup
import re
import pymysql
import time

def inSQL(title,detail,owner,part,address,prdata): #存入MySQL
    cursor = db.cursor()
    sql = f"INSERT INTO bsanjuke(title,detail,owner,part,address,prdata) values {title,detail,owner,part,address,prdata}"
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

def getHTML(url):
    headers ={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.75 Safari/537.36'}
    r = requests.get(url,headers=headers)
    return r.text

def getHouse(html):
    soup = BeautifulSoup(html, 'lxml')
    for i in soup.find_all(class_='house-details'):
        #1.title
        title = i.a.string.strip()
        #2.detail
        delist = list(j.text.strip() for j in i.select('.details-item'))
        detail_owner = delist[0].split('\ue147')
        detail = detail_owner[0]
        owner = detail_owner[1]
        part_add = re.sub('\s+','::',delist[1])
        part_a_list = part_add.split('::')
        part = part_a_list[0]
        address = part_a_list[1]
        #price
        prdata = i.find_next_sibling().text.strip()
        print('bs is ok')
        inSQL(title,detail,owner,part,address,prdata)

def main():
    url = 'https://chongqing.anjuke.com/sale/bishanqu/'
    
    for i in range(1,51):
        if i == 1:
            url1 = url
            html = getHTML(url1)
            getHouse(html)
            print(url1)
        else:
            url1 = f"{url}p{i}/#filtersort"
            time.sleep(1)
            html = getHTML(url1)
            getHouse(html)
            print(url1)
    db.close()

db = pymysql.connect(host='localhost', user='root', password='zhaoqi', port=3306, db='spiders')
main()
    