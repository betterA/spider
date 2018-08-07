网易云热门评论爬虫

学会使用F12

F12 --> Network  在下面寻找![2018-08-06 16-45-28屏幕截图](/home/tewic/图片/2018-08-06 16-45-28屏幕截图.png)

看到hot Comments 这就是我们需要的数据

点击　headers看见是POST 类型 　看见 Form Data 看表数据

我的所有Form Data 都是一样的。

```python
import requests
PARAM ={ 'params': '/GPkot9IYTu/hWGjiPZ2No0aafK7NaPaA/LOuEDOMZvNgQkQKGUaOv6VhvE7wVqKnY1sQ66rCS5oB9eBjarR8WLFVIiJgNTuUK53MrSnhyN+eypMqwUFFhth/QFO7ozyml6D/UVyBf/faHTdMV9fUUBuaytFqhJqir/e8rYVQ6YJfZyTc5HNKR3TJYMdmn5V',
  'encSecKey':'6fe5394c076bc964d7ad14feaf28d8c11376b136129190475ddd65f52cb6f85d85165b354952a7fdb97702892d8fd3f9587188ac186eb29dd095dc2759e8ac9a80ed84ad6f25ff34a0596b1812a964aea6ba01fe6870dbec5394817f930c5ec47ad6be829e1ed99a672862623327a68253a051bd886e1c32cf49db8d45a0f971'}
HEADERS = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'}
def get_music_page(url,title):
    response = requests.post(url,PARAM,headers=HEADERS)
    r_json = response.json()
    hot_content = r_json.get("hotComments")
    contents = [item.get('content') for item in hot_content]
    return {
            'title':title,
            'content':contents
        }
```

我选择　爬取我的歌单内容

进入我的歌单页面:

我没有找到我要的歌单数据

突然　右键--> 框架源码有我想要的内容

```
网页源码：view-source:https://music.163.com/#/playlist?id=2168333836
框架源码：view-source:https://music.163.com/playlist?id=2168333836
url 有差异　所有我知道怎么做了
```



```python
def get_music_list(url):
    #url-->https://music.163.com/playlist?id=2168333836
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
```

所有代码

```python
import requests
import re
from bs4 import BeautifulSoup
import pymongo

PARAM ={ 'params': '/GPkot9IYTu/hWGjiPZ2No0aafK7NaPaA/LOuEDOMZvNgQkQKGUaOv6VhvE7wVqKnY1sQ66rCS5oB9eBjarR8WLFVIiJgNTuUK53MrSnhyN+eypMqwUFFhth/QFO7ozyml6D/UVyBf/faHTdMV9fUUBuaytFqhJqir/e8rYVQ6YJfZyTc5HNKR3TJYMdmn5V',
  'encSecKey':'6fe5394c076bc964d7ad14feaf28d8c11376b136129190475ddd65f52cb6f85d85165b354952a7fdb97702892d8fd3f9587188ac186eb29dd095dc2759e8ac9a80ed84ad6f25ff34a0596b1812a964aea6ba01fe6870dbec5394817f930c5ec47ad6be829e1ed99a672862623327a68253a051bd886e1c32cf49db8d45a0f971'}
HEADERS = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36'}

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
        content_url = 				f'https://music.163.com/weapi/v1/resource/comments/R_SO_4_{music_id[0]}?csrf_token='
        print(content_url)
        title = i.string
        result = get_music_page(content_url,title)
        if result:
            save_to_mongo(result)

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
         print('存入成功')
         return True
    return False


client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
url = 'https://music.163.com/playlist?id=2168333836'
get_music_list(url)
```

